import datetime
from string import Template

import robocompdsl.dsl_parsers.parsing_utils as p_utils
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils
from robocompdsl.templates.common.templatedict import TemplateDict

DSR_SAVE = """\
/*
for (auto const& [name, g] : Graphs) {
    g->write_to_json_file("./"+agent_name+"_"+name+".json");
}
*/
"""

DSR_CONNECTIONS= """\
//Subscription to DSR graph update signals. 
// If multiple graphs exist, it is necessary to specify the graph name 
// using 'Graphs.at("name")' to connect its signals to the Worker's slots.
//connect(Graphs.at("").get(), &DSR::DSRGraph::update_node_signal, this, &SpecificWorker::modify_node_slot);
//connect(Graphs.at("").get(), &DSR::DSRGraph::update_edge_signal, this, &SpecificWorker::modify_edge_slot);
//connect(Graphs.at("").get(), &DSR::DSRGraph::update_node_attr_signal, this, &SpecificWorker::modify_node_attrs_slot);
//connect(Graphs.at("").get(), &DSR::DSRGraph::update_edge_attr_signal, this, &SpecificWorker::modify_edge_attrs_slot);
//connect(Graphs.at("").get(), &DSR::DSRGraph::del_edge_signal, this, &SpecificWorker::del_edge_slot);
//connect(Graphs.at("").get(), &DSR::DSRGraph::del_node_signal, this, &SpecificWorker::del_node_slot);
"""


CUSTOM_WIDGET= """\
/***
Custom Widget
In addition to the predefined viewers, Graph Viewer allows you to add various widgets designed by the developer.
The add_custom_widget_to_dock method is used. This widget can be defined like any other Qt widget,
either with a QtDesigner or directly from scratch in a class of its own.
The add_custom_widget_to_dock method receives a name for the widget and a reference to the class instance.
***/
//If you have more than one graph, you need to connect to the specific graph with the name
//graph_viewers.at("")->add_custom_widget_to_dock("CustomWidget", &custom_widget);
"""

class specificworker_cpp(TemplateDict):
    def __init__(self, component):
        super(specificworker_cpp, self).__init__()
        self.component = component
        self['dsr_save'] = self.dsr_save()
        self['dsr_connections'] = self.dsr_connections()
        self['dsr_custom_widget'] = self.dsr_custom_widget()


    def dsr_save(self):
        result = ""
        if self.component.dsr:
            result += DSR_SAVE
        return result
    
    def dsr_connections(self):
        result = ""
        if self.component.dsr:
            result += DSR_CONNECTIONS
        return result
    
    def dsr_custom_widget(self):
        result = ""
        if self.component.dsr:
            result += CUSTOM_WIDGET
        return result


