import os
import traceback
from collections import OrderedDict

from pyparsing import Suppress, Word, CaselessKeyword, alphas, alphanums, CharsNotIn, Group, ZeroOrMore, Optional, \
    delimitedList, cppStyleComment

from dsl_parsers.dsl_parser_abstract import DSLParserTemplate
from dsl_parsers.parsing_utils import isAGM2Agent, isAGM2AgentROS, communicationIsIce, isAGM1Agent, \
    generateRecursiveImports


class CDSLParser(DSLParserTemplate):
    def __init__(self, include_directories = []):
        super(CDSLParser, self).__init__()
        self._include_directories = include_directories

    def _create_parser(self):
        OBRACE, CBRACE, SEMI, OPAR, CPAR = list(map(Suppress, "{};()"))
        QUOTE = Suppress(Word("\""))

        # keywords
        (IMPORT, COMMUNICATIONS, LANGUAGE, COMPONENT, CPP, CPP11, GUI, QWIDGET, QMAINWINDOW, QDIALOG, QT,
         PYTHON, REQUIRES, IMPLEMENTS, SUBSCRIBESTO, PUBLISHES, OPTIONS, TRUE, FALSE,
         INNERMODELVIEWER, STATEMACHINE, VISUAL) = list(map(CaselessKeyword, """
        import communications language component cpp cpp11 gui QWidget QMainWindow QDialog Qt 
        python requires implements subscribesTo publishes options true false
        InnerModelViewer statemachine visual""".split()))

        identifier = Word(alphas + "_", alphanums + "_")
        PATH = CharsNotIn("\";")

        # Imports
        idslImport = Group(Suppress(IMPORT) - QUOTE + PATH.setResultsName('idsl_path') - QUOTE + SEMI)

        idslImports = ZeroOrMore(idslImport).setResultsName("imports")

        commType = Optional(OPAR - (CaselessKeyword("ice") | CaselessKeyword("ros")).setResultsName("type") + CPAR)

        implementsList = Optional(
            IMPLEMENTS - Group(delimitedList(identifier.setResultsName("impIdentifier") + commType)).setResultsName(
                "implements") + SEMI)

        requiresList = Optional(
            REQUIRES - Group(delimitedList(identifier.setResultsName("reqIdentifier") + commType)).setResultsName(
                "requires") + SEMI)

        subscribesList = Optional(
            SUBSCRIBESTO - Group(delimitedList(identifier.setResultsName("subIdentifier") + commType)).setResultsName(
                "subscribesTo") + SEMI)

        publishesList = Optional(
            PUBLISHES - Group(delimitedList(identifier.setResultsName("pubIdentifier") + commType)).setResultsName(
                "publishes") + SEMI)

        communicationList = Group(implementsList & requiresList & subscribesList & publishesList).setResultsName(
            "communications")
        communications = COMMUNICATIONS.suppress() - OBRACE + communicationList + CBRACE + SEMI

        # Language
        language_options = (CPP | CPP11 | PYTHON).setResultsName('language')
        language = LANGUAGE.suppress() - language_options - SEMI

        # InnerModelViewer
        innermodelviewer = Group(Optional(INNERMODELVIEWER.suppress() - (TRUE | FALSE) + SEMI))('innermodelviewer')
        # GUI
        gui_options = QWIDGET | QMAINWINDOW | QDIALOG
        gui = Group(Optional(GUI.suppress() - QT + OPAR - gui_options('gui_options') - CPAR + SEMI))
        # additional options
        options = Group(Optional(OPTIONS.suppress() - identifier + ZeroOrMore(Suppress(Word(',')) + identifier) + SEMI))
        statemachine = Group(
            Optional(STATEMACHINE.suppress() - QUOTE + CharsNotIn("\";").setResultsName('machine_path') + QUOTE + Optional(VISUAL.setResultsName('visual').setParseAction(lambda t: True))+ SEMI))

        # Component definition
        componentContents = Group(
            communications - language + Optional(gui('gui')) + Optional(options('options')) + Optional(innermodelviewer) + Optional(statemachine('statemachine'))).setResultsName(
            "content")
        component = Group(
            COMPONENT.suppress() - identifier("name") + OBRACE + componentContents + CBRACE + SEMI).setResultsName(
            "component")

        CDSL = idslImports - component
        CDSL.ignore(cppStyleComment)
        return CDSL

    def string_to_struct(self, string, **kwargs):
        parsing_result = self.parse_string(string)
        component = OrderedDict()
        # print 'parseCDSL.component', includeDirectories
        if self._include_directories == None:
            self._include_directories = []
        if "include_directories" in kwargs:
            self._include_directories = kwargs["include_directories"]
        # Set options
        component['options'] = []
        try:
            for op in parsing_result['component']['content']['options']:
                component['options'].append(op.lower())
        except:
            traceback.print_exc()

        # Component name
        component['name'] = parsing_result['component']['name']
        # Imports
        component['imports'] = []
        component['recursiveImports'] = []
        try:
            imprts = [path['idsl_path'] for path in parsing_result.asDict()["imports"]]
        except:
            parsing_result['imports'] = []
            imprts = []
        if isAGM1Agent(component):
            imprts.extend(['AGMExecutive.idsl', 'AGMCommonBehavior.idsl', 'AGMWorldModel.idsl', 'AGMExecutiveTopic.idsl'])
        if isAGM2Agent(component):
            imprts.extend(['AGM2.idsl'])
        iD = self._include_directories + ['/opt/robocomp/interfaces/IDSLs/',
                                   os.path.expanduser('~/robocomp/interfaces/IDSLs/')]
        for imp in sorted(imprts):
            import_basename = os.path.basename(imp)
            component['imports'].append(import_basename)
        component['recursiveImports'] = generateRecursiveImports(component['imports'], self._include_directories)
        # Language
        component['language'] = parsing_result['component']['content']['language']
        # Statemachine
        component['statemachine'] = None
        try:
            statemachine = parsing_result['component']['content']['statemachine']['machine_path']
            component['statemachine'] = statemachine
        except:
            pass
        try:
            statemachine_visual = parsing_result['component']['content']['statemachine']['visual']
        except:
            component['statemachine_visual'] = False
        else:
            component['statemachine_visual'] = statemachine_visual

        # innermodelviewer
        component['innermodelviewer'] = False
        try:
            component['innermodelviewer'] = 'innermodelviewer' in [x.lower() for x in component['options']]
            pass
        except:
            pass
        # GUI
        component['gui'] = None
        try:
            uiT = parsing_result['component']['content']['gui'][0]
            uiI = parsing_result['component']['content']['gui']['gui_options']
            if uiT.lower() == 'qt' and uiI in ['QWidget', 'QMainWindow', 'QDialog']:
                component['gui'] = [uiT, uiI]
                pass
            else:
                print(('Wrong UI specification', parsing_result['properties']['gui']))
                sys.exit(1)
        except:
            # TODO: check exceptions and do something when accessing gui options fails.
            pass

        # Communications
        component['rosInterfaces'] = []
        component['iceInterfaces'] = []
        component['implements'] = []
        component['requires'] = []
        component['publishes'] = []
        component['subscribesTo'] = []
        component['usingROS'] = False
        ####################
        com_types = ['implements', 'requires', 'publishes', 'subscribesTo']
        communications = parsing_result['component']['content']['communications']
        for comm_type in com_types:
            if comm_type in communications:
                interfaces = sorted(communications[comm_type])
                for interface in interfaces:
                    component[comm_type].append(interface)
                    if communicationIsIce(interface):
                        component['iceInterfaces'].append(interface)
                    else:
                        component['rosInterfaces'].append(interface)
                        component['usingROS'] = True
        # Handle options for communications
        if isAGM1Agent(component):
            component['iceInterfaces'] += ['AGMCommonBehavior', 'AGMExecutive', 'AGMExecutiveTopic', 'AGMWorldModel']
            if not 'AGMCommonBehavior' in component['implements']:
                component['implements'] = ['AGMCommonBehavior'] + component['implements']
            if not 'AGMExecutive' in component['requires']:
                component['requires'] = ['AGMExecutive'] + component['requires']
            if not 'AGMExecutiveTopic' in component['subscribesTo']:
                component['subscribesTo'] = ['AGMExecutiveTopic'] + component['subscribesTo']
        if isAGM2Agent(component):
            if isAGM2AgentROS(component):
                component['usingROS'] = True
                agm2agent_requires = [['AGMDSRService', 'ros']]
                agm2agent_subscribesTo = [['AGMExecutiveTopic', 'ros'], ['AGMDSRTopic', 'ros']]
                if not 'AGMDSRService' in component['rosInterfaces']: component['rosInterfaces'].append('AGMDSRService')
                if not 'AGMDSRTopic' in component['rosInterfaces']: component['rosInterfaces'].append('AGMDSRTopic')
                if not 'AGMExecutiveTopic' in component['rosInterfaces']: component['rosInterfaces'].append(
                    'AGMExecutiveTopic')
            else:
                agm2agent_requires = [['AGMDSRService', 'ice']]
                agm2agent_subscribesTo = [['AGMExecutiveTopic', 'ice'], ['AGMDSRTopic', 'ice']]
                if not 'AGMDSRService' in component['iceInterfaces']: component['iceInterfaces'].append('AGMDSRService')
                if not 'AGMDSRTopic' in component['iceInterfaces']: component['iceInterfaces'].append('AGMDSRTopic')
                if not 'AGMExecutiveTopic' in component['iceInterfaces']: component['iceInterfaces'].append(
                    'AGMExecutiveTopic')

            # AGM2 agents REQUIRES
            for agm2agent_req in agm2agent_requires:
                if not agm2agent_req in component['requires']:
                    component['requires'] = [agm2agent_req] + component['requires']
            # AGM2 agents SUBSCRIBES
            for agm2agent_sub in agm2agent_subscribesTo:
                if not agm2agent_sub in component['subscribesTo']:
                    component['subscribesTo'] = [agm2agent_sub] + component['subscribesTo']
        self.struct = component
        return component

    def __str__(self):
        struct_str= ""
        struct_str+= 'Component %s\n' % self.struct['name']

        struct_str+= '\tImports:\n'
        for imp in self.struct['imports']:
            struct_str+= '\t\t %s\n'% imp
        # Language
        struct_str+= '\tLanguage:'
        struct_str+= '\t\t %s\n' %self.struct['language']
        # GUI
        struct_str+= '\tGUI:\n'
        struct_str+= '\t\t %\n' % self.struct['gui']
        # Communications
        struct_str+= '\tCommunications:\n'
        struct_str+= '\t\tImplements %s \n'% self.struct['implements']
        struct_str+= '\t\tRequires %s\n'% self.struct['requires']
        struct_str+= '\t\tPublishes %s\n'% self.struct['publishes']
        struct_str+= '\t\tSubscribes %s\n'% self.struct['subscribesTo']
        return struct_str
