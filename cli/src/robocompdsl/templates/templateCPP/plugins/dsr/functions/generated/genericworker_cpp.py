import datetime
from string import Template
from robocompdsl.dsl_parsers.parsing_utils import get_name_number, communication_is_ice
from robocompdsl.templates.common.templatedict import TemplateDict

DSR_DELETE = """\
for (auto& [name, graphPtr] : Graphs) {
    if (!graphPtr) continue;
    auto grid_nodes = graphPtr->get_nodes_by_type("grid");
    for (auto grid : grid_nodes) {
        graphPtr->delete_node(grid);
    }
}
"""

DSR_SET_PARAMS = """\
agent_name = this->configLoader.get<std::string>("Agent.name");
agent_id = this->configLoader.get<int>("Agent.id");

// Create graph
auto surNames = configLoader.getSurNames("Agent");
if (surNames.empty()) {
    int domain = this->configLoader.exists("Agent.domain") ? this->configLoader.get<int>("Agent.domain") : 0;
    auto [it, inserted] = Graphs.emplace("", std::make_shared<DSR::DSRGraph>(0, agent_name, agent_id, 
                                    this->configLoader.get<std::string>("Agent.configFile"), 
                                    true, domain));
    std::cout << "Graph loaded" << std::endl;
    G = it->second;
} 
else {
    std::cout << "Multiple graphs found: " << surNames.size() << std::endl;
    for (std::string_view surName : surNames) {
        std::string name{surName};
        std::string prefix = "Agent." + name;

        Graphs.emplace(name, std::make_shared<DSR::DSRGraph>(0, agent_name, agent_id, 
                                        configLoader.get<std::string>(prefix + ".configFile"), 
                                        true, 
                                        configLoader.get<int>(prefix + ".domain")));
        std::cout << "Graph " << name << " loaded" << std::endl;
    }
    G = Graphs.at(std::string(surNames.front()));
}
"""

DSR_INITIALIZE = """\
for (const auto& [name, Graph] : Graphs) {
    std::unique_ptr<QMainWindow> window = std::make_unique<QMainWindow>();
    window->setWindowTitle(QString("%1-%2|%3").arg(QString::fromStdString(agent_name)).arg(agent_id).arg(QString::fromStdString(name)));

    std::string prefix = "Agent";
    if (Graphs.size()>1)
        prefix += "." +name;

    std::shared_ptr<DSR::DSRViewer> viewer = setupViewer(Graph, prefix, window.get());
    if (viewer){
        graph_viewers.emplace(name, std::move(viewer));
        windows.emplace(name, std::move(window));
    }
}
"""

DSR_VIEWER = """\
std::shared_ptr<DSR::DSRViewer> GenericWorker::setupViewer(std::shared_ptr<DSR::DSRGraph> graph, const std::string& prefix, QMainWindow* parent)
{
    int current_opts = 0;
    DSR::DSRViewer::view main = DSR::DSRViewer::view::none;
    using opts = DSR::DSRViewer::view;

    // Estructura de datos para iterar las opciones (más limpio que muchos IFs)
    const std::vector<std::pair<std::string, opts>> options = {
        {"tree", opts::tree}, {"graph", opts::graph}, 
        {"2d", opts::scene}
    };

    for (const auto& [suffix, flag] : options) {
        if (this->configLoader.get<bool>(prefix + "." + suffix)) {
            current_opts |= flag;
            if (suffix == "graph") main = opts::graph;
        }
    }
    if (current_opts!=0)
    	return std::make_shared<DSR::DSRViewer>(parent, graph, current_opts, main);
	else
		return nullptr;
};
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
        if self.component.dsr:
            result += DSR_VIEWER
        return result
