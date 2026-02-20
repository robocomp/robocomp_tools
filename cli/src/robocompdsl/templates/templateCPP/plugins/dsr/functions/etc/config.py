from string import Template

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.common.templatedict import TemplateDict


DSR_CONFIG_STR = """\
# --- Common Agent Data ---
Agent.id = 0 # Change id
Agent.name = "${name}"

# --- Single Instance Configuration ---
# Use this if you only have one graph.
Agent.configFile = ""
Agent.domain = 0
Agent.tree = true
Agent.graph = true
Agent.2d = true
Agent.3d = true

# --- Multiple Instance Template ---
# If you define sub-instances, the single instance config above will be ignored.
# Agent.instance_name.configFile = ""
# Agent.instance_name.domain = 1
# Agent.instance_name.tree = true
# Agent.instance_name.graph = true
# Agent.instance_name.2d = true
# Agent.instance_name.3d = true
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

