import datetime

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils
from robocompdsl.templates.common.templatedict import TemplateDict

DSR_INCLUDES_STR = """\
#include "dsr/api/dsr_api.h"
#include "dsr/gui/dsr_gui.h"
#include <doublebuffer/DoubleBuffer.h>
"""

DSR_ATTRIBUTES = """\
// DSR graph
std::shared_ptr<DSR::DSRGraph> G;

//DSR params
std::string agent_name;
int agent_id;
int current_opts = 0;
DSR::DSRViewer::view main = DSR::DSRViewer::view::none;
"""

DSR_VIEWER_ATTRIBUTES = """\
// DSR graph viewer
std::unique_ptr<DSR::DSRViewer> graph_viewer;
QHBoxLayout mainLayout;
"""

class genericworker_h(TemplateDict):

    def __init__(self, component):
        super(genericworker_h, self).__init__()
        self.component = component
        self['dsr_includes'] = self.dsr_includes()
        self['dsr_attributes'] = self.dsr_attributes()
        self['dsr_viewer_attributes'] = self.dsr_viewer_attributes()

    def dsr_includes(self):
        result = ""
        if self.component.dsr:
            result = DSR_INCLUDES_STR
        return result

    def dsr_attributes(self):
        result = ""
        if self.component.dsr:
            result = DSR_ATTRIBUTES
        return result

    def dsr_viewer_attributes(self):
        result = ""
        if self.component.dsr and self.component.gui is not None and "QMainWindow" in self.component.gui:
            result = DSR_VIEWER_ATTRIBUTES
        return result