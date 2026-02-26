from string import Template

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.common.templatedict import TemplateDict


DSR_CONFIG_STR = """\
# --- Common Agent Data ---
[Agent]
id = 0 # Change id
name = "${name}"

# --- Single Instance Configuration ---
# Use this if you only have one graph.
configFile = ""
domain = 0
tree = true
graph = true
2d = true
3d = true

# --- Multiple Instance Template ---
# If you define multiple instances, the single instance config above will be ignored.
# [Agent.instance_name]
# configFile = ""
# domain = 1
# tree = true
# graph = true
# 2d = true
# 3d = true
"""

class etc_config_toml(TemplateDict):
    def __init__(self, component):
        super(etc_config_toml, self).__init__()
        self.component = component
        self['dsr_config'] = self.dsr_config()

    def dsr_config(self):
        result = ""
        if self.component.dsr:
            result += Template(DSR_CONFIG_STR).substitute(name=self.component.name)
        return result

