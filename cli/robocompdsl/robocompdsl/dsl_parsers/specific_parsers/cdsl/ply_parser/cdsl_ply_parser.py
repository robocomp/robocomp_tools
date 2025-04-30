import os

from robocompdsl.dsl_parsers.dsl_parser_abstract import DSLParserTemplate
from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice
from robocompdsl.dsl_parsers.specific_parsers.cdsl.componentinspections import ComponentInspections
from robocompdsl.dsl_parsers.specific_parsers.cdsl.ply_parser.ply_parser_yacc import CCDSLPlyParser


class CDSLParser(DSLParserTemplate):
    def __init__(self, include_directories = []):
        super(CDSLParser, self).__init__()
        self._include_directories = include_directories

    def _create_parser(self):
        CDSL = CCDSLPlyParser()
        return CDSL

    def string_to_struct(self, dsl_string, **kwargs):
        component = self.parse_string(dsl_string)
        if component is None:
            raise ValueError("There was some problem parsing the component file.")
        inspections = ComponentInspections()
        inspections.check_all_inspections(component)

        # print 'parseCDSL.component', includeDirectories
        if self._include_directories is None:
            self._include_directories = []

        if "include_directories" in kwargs:
            self._include_directories = kwargs["include_directories"]

        if 'imports' in component:
            imprts = component.imports
        else:
            imprts = []
        iD = self._include_directories + ['/opt/robocomp/interfaces/IDSLs/',
                                          os.path.expanduser('~/robocomp/interfaces/IDSLs/')]

        component.imports = list(map(os.path.basename, imprts))
        from robocompdsl.dsl_parsers.idslpool import idsl_pool
        component.imports = idsl_pool.update_with_idsls(list(component.imports),
                                                                   self._include_directories)

        component.statemachine_visual = False
        if isinstance(component.statemachine, list):
            if len(component.statemachine) > 1:
                if component.statemachine[1]:
                    component.statemachine_visual = True
            component.statemachine = component.statemachine[0]

        try:
            component.innermodelviewer = 'innermodelviewer' in [x.lower() for x in component.options]
        except:
            pass


        com_types = ['implements', 'requires', 'publishes', 'subscribesTo']
        for comm_type in com_types:
            if comm_type in component:
                # TODO: FIX when interfaces are tuples with name and type!
                for interface in sorted(component[comm_type]):
                    if communication_is_ice(interface):
                        component.iceInterfaces.append(interface)
                    else:
                        component.rosInterfaces.append(interface)
                        component.usingROS = True
        # Handle options for communications
        self.struct = component
        return component
