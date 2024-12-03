from string import Template

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.common.templatedict import TemplateDict


DSR_VIEWER_CONFIG_STR = """\
[ViewAgent]
tree = true
graph = true
2d = true
3d = true
"""

class etc_config_toml(TemplateDict):
    def __init__(self, component):
        super(etc_config_toml, self).__init__()
        self.component = component
        self['dsr_viewer_config'] = self.dsr_viewer_config()

    def dsr_viewer_config(self):
        result = ""
        if self.component.dsr and self.component.gui is not None and "QMainWindow" in self.component.gui:
            result = DSR_VIEWER_CONFIG_STR
        return result

