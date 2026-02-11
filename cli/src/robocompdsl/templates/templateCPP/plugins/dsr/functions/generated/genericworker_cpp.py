import datetime
from string import Template
from robocompdsl.dsl_parsers.parsing_utils import get_name_number, communication_is_ice
from robocompdsl.templates.common.templatedict import TemplateDict

DSR_DELETE = """\
auto grid_nodes = G->get_nodes_by_type("grid");
for (auto grid : grid_nodes)
{
	G->delete_node(grid);
}
G.reset();
"""

DSR_SET_PARAMS = """\
agent_name = this->configLoader.get<std::string>("Agent.name");
agent_id = this->configLoader.get<int>("Agent.id");
"""

DSR_INITIALIZE = """\
// Create graph
G = std::make_shared<DSR::DSRGraph>(0, agent_name, agent_id, this->configLoader.get<std::string>("Agent.configFile")); // Init nodes
std::cout<< "Graph loaded" << std::endl;  
"""

DSR_VIEWER = """\
// Graph viewer
using opts = DSR::DSRViewer::view;
if(this->configLoader.get<bool>("ViewAgent.tree"))
{
    current_opts = current_opts | opts::tree;
}
if(this->configLoader.get<bool>("ViewAgent.graph"))
{
    current_opts = current_opts | opts::graph;
    main = opts::graph;
}
if(this->configLoader.get<bool>("ViewAgent.2d"))
{
    current_opts = current_opts | opts::scene;
}
if(this->configLoader.get<bool>("ViewAgent.3d"))
{
    current_opts = current_opts | opts::osg;
}
setWindowTitle(QString::fromStdString(agent_name + "-") + QString::number(agent_id));
"""

class genericworker_cpp(TemplateDict):
    def __init__(self, component):
        super(genericworker_cpp, self).__init__()
        self.component = component
        self['dsr_set_params'] = self.dsr_set_params()
        self['dsr_initialize'] = self.dsr_initialize()
        self['dsr_viewer'] = self.dsr_viewer()
        self['dsr_delete'] = self.dsr_delete()

    def dsr_delete(self):
        result = ""
        if self.component.dsr:
            result += DSR_DELETE
        return result

    def dsr_set_params(self):
        result = ""
        if self.component.dsr:
            result += DSR_SET_PARAMS
        return result

    def dsr_initialize(self):
        result = ""
        if self.component.dsr:
            result += DSR_INITIALIZE
        return result
    
    def dsr_viewer(self):
        result = ""
        if self.component.dsr and self.component.gui is not None and "QMainWindow" in self.component.gui:
            result += DSR_VIEWER
        return result
