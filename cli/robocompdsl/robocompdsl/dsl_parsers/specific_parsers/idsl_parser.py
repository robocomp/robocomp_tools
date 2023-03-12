from collections import OrderedDict
from operator import attrgetter

from pyparsing import Suppress, Word, alphas, alphanums, Group, \
    OneOrMore, ZeroOrMore, Optional, cppStyleComment, Literal, CharsNotIn

from robocompdsl.dsl_parsers.dsl_parser_abstract import DSLParserTemplate
from robocompdsl.dsl_parsers.specific_parsers.interfacefacade import InterfaceFacade
from robocompdsl.logger import logger

class IDSLParser(DSLParserTemplate):
    def __init__(self):
        super(IDSLParser, self).__init__()

    def _create_parser(self):

        semicolon = Suppress(Word(";"))
        quote = Suppress(Word("\""))
        op = Suppress(Word("{"))
        cl = Suppress(Word("}"))
        opp = Suppress(Word("("))
        clp = Suppress(Word(")"))
        lt = Suppress(Word("<"))
        gt = Suppress(Word(">"))
        eq = Suppress(Word("="))
        identifier = Word(alphas + "_", alphanums + "_")
        typeIdentifier = Word(alphas + "_", alphanums + "_:")
        structIdentifer = Group(
            typeIdentifier.setResultsName('type') + identifier.setResultsName('identifier') + Optional(eq) + Optional(
                CharsNotIn(";").setResultsName('defaultValue')) + semicolon)
        structIdentifers = Group(OneOrMore(structIdentifer))

        ## Imports
        idslImport = Suppress(Word("import")) + quote + CharsNotIn("\";").setResultsName('path') + quote + semicolon
        idslImports = ZeroOrMore(idslImport)

        structDef = Word("struct").setResultsName('type') + identifier.setResultsName(
            'name') + op + structIdentifers.setResultsName("structIdentifiers") + cl + semicolon
        dictionaryDef = Word("dictionary").setResultsName('type') + lt + CharsNotIn("<>").setResultsName(
            'content') + gt + identifier.setResultsName('name') + semicolon
        sequenceDef = Word("sequence").setResultsName('type') + lt + typeIdentifier.setResultsName(
            'typeSequence') + gt + identifier.setResultsName('name') + semicolon
        enumDef = Word("enum").setResultsName('type') + identifier.setResultsName('name') + op + CharsNotIn(
            "{}").setResultsName('content') + cl + semicolon
        exceptionDef = Word("exception").setResultsName('type') + identifier.setResultsName('name') + op + CharsNotIn(
            "{}").setResultsName('content') + cl + semicolon

        raiseDef = Suppress(Word("throws")) + typeIdentifier + ZeroOrMore(Literal(',') + typeIdentifier)
        decoratorDef = Literal('idempotent') | Literal('out')
        retValDef = typeIdentifier.setResultsName('ret')

        firstParam = Group(Optional(decoratorDef.setResultsName('decorator')) + typeIdentifier.setResultsName(
            'type') + identifier.setResultsName('name'))
        nextParam = Suppress(Word(',')) + firstParam
        params = firstParam + ZeroOrMore(nextParam)

        remoteMethodDef = Group(Optional(decoratorDef.setResultsName('decorator')) + retValDef.setResultsName(
            'ret') + typeIdentifier.setResultsName('name') + opp + Optional(params).setResultsName(
            'params') + clp + Optional(raiseDef.setResultsName('raise')) + semicolon)
        interfaceDef = Word('interface').setResultsName('type') + typeIdentifier.setResultsName('name') + op + Group(
            ZeroOrMore(remoteMethodDef)).setResultsName('methods') + cl + semicolon

        moduleContent = Group(structDef | enumDef | exceptionDef | dictionaryDef | sequenceDef | interfaceDef)
        module = Suppress(Word("module")) + identifier.setResultsName("name") + op + ZeroOrMore(
            moduleContent).setResultsName("contents") + cl + semicolon

        IDSL = idslImports.setResultsName("imports") + module.setResultsName("module")
        IDSL.ignore(cppStyleComment)
        return IDSL

    def string_to_struct(self, string, **kwargs) -> InterfaceFacade:
        logger.debug("Parsing IDSL")
        parsing_result = self.parse_string(string)
        interface = InterfaceFacade()


        self.include_directories = []
        if "include_directories" in kwargs:
            self.include_directories = kwargs["include_directories"]
        logger.debug(f"\twith include_directories: {self.include_directories}")
        # Hack to make robocompdsl work with pyparsing > 2.2
        try:
            interface.name = parsing_result['module']['name']
        except KeyError:
            interface.name = parsing_result['name']
        logger.debug(f"\twith name: {interface.name}")

        interface.imports = []
        interface.recursive_imports = []
        if 'imports' in parsing_result:
            # print interface.name, parsing_result['imports']
            interface.imports = parsing_result['imports'].asList()
            logger.debug(f"\twith imports: {interface.imports}")
            from robocompdsl.dsl_parsers.idslpool import idsl_pool
            interface.recursive_imports = idsl_pool.update_with_idsls(list(parsing_result['imports']))
            logger.debug(f"\twith recursive_imports: {interface.recursive_imports}")

        # INTERFACES DEFINED IN THE MODULE
        interface.interfaces = []
        # Hack to make robocompdsl work with pyparsing > 2.2
        try:
            contents = parsing_result['module']['contents']
        except KeyError:
            contents = parsing_result['contents']

        for contentDef in contents:
            if contentDef[0] == 'interface':
                # interface_struct = {'name': contentDef[1], 'methods': OrderedDict()}
                # for method in sorted(contentDef.methods, key=attrgetter('name')):
                #     interface_struct.methods[method.name] = {}
                #
                #     interface_struct.methods[method.name]['name'] = method.name
                #     try:
                #         interface_struct.methods[method.name]['decorator'] = method.decorator
                #     except KeyError:
                #         interface_struct.methods[method.name]['decorator'] = ''
                #
                #     interface_struct.methods[method.name]['return'] = method.ret
                #
                #     params = []
                #     try:
                #         for p in method.params:
                #             try:
                #                 params.append({'decorator': p.decorator, 'type': p.type, 'name': p.name})
                #             except KeyError:
                #                 params.append({'decorator': 'none', 'type': p.type, 'name': p.name})
                #     except KeyError:
                #         pass
                #     interface_struct.methods[method.name]['params'] = params
                #
                #     try:
                #         interface_struct.methods[method.name]['throws'] = method.raise.asList()
                #     except KeyError:
                #         interface_struct.methods[method.name]['throws'] = 'nothing'
                interface.interfaces.append(contentDef.asDict())
        logger.debug(f"\twith {len(interface.interfaces)} interfaces")

        # TYPES DEFINED IN THE MODULE
        interface.types = []
        # print '---\n---\nPARSE IDSL TYPES'
        for contentDef in contents:
            # print contentDef[0]
            if contentDef[0] in ['enum', 'struct', 'exception']:
                # typedef = {'name': contentDef[1], 'type': contentDef[0]}
                typedef = contentDef.asDict()

                # print typedef
                interface.types.append(typedef)
            elif contentDef[0] in ['sequence', 'dictionary']:
                typedef = contentDef.asDict()
                # print typedef
                interface.types.append(typedef)
            elif contentDef[0] in ['interface']:
                pass
            else:
                print(('Unknown module content', contentDef))

        # SEQUENCES DEFINED IN THE MODULE
        interface.sequences = []
        interface.simpleSequences = []
        for contentDef in contents:
            if contentDef['type'] == 'sequence':
                seq_def = {'name': interface.name + "/" + contentDef['name'], 'type': contentDef['type'], 'typeSequence': contentDef['typeSequence']}
                simple_seq_def = {'name': interface.name, 'strName': contentDef['name']}
                # print structdef
                interface.sequences.append(seq_def)
                interface.simpleSequences.append(simple_seq_def)

        # STRUCTS DEFINED IN THE MODULE
        interface.structs = []
        interface.simpleStructs = []
        for contentDef in contents:
            if contentDef['type'] == 'struct':
                structdef = {'name': interface.name + "/" + contentDef['name'], 'type': contentDef['type'], 'structIdentifiers': contentDef['structIdentifiers'].asList()}
                simple_struct_def = {'name': interface.name, 'strName': contentDef['name']}
                # print structdef
                interface.structs.append(structdef)
                interface.simpleStructs.append(simple_struct_def)

        self.struct = interface
        return interface
