from string import Template

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.common.templatedict import TemplateDict


DSR_CONFIG_STR = """\
# Change id
Agent.id = 0
Agent.name = "${name}"
Agent.configFile = ""
"""

class etc_config(TemplateDict):
    def __init__(self, component):
        super(etc_config, self).__init__()
        self.component = component
        self['dsr_config'] = self.dsr_config()

    def dsr_config(self):
        result = ""
        if self.component.dsr:
            result += Template(DSR_CONFIG_STR).substitute(name=self.component.name)
        return result

