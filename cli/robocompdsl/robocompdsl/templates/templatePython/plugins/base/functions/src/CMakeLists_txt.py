from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice
from robocompdsl.templates.common.templatedict import TemplateDict


class src_CMakeLists_txt(TemplateDict):
    def __init__(self, component):
        super(src_CMakeLists_txt, self).__init__()
        self.component = component
        self['component_name'] = self.component.name
