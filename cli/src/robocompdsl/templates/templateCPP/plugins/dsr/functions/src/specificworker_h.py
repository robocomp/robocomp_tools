import datetime

import robocompdsl.dsl_parsers.parsing_utils as p_utils
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils
from robocompdsl.templates.common.templatedict import TemplateDict

DSR_SLOTS = """\
void modify_node_slot(std::uint64_t, const std::string &type){};
void modify_node_attrs_slot(std::uint64_t id, const std::vector<std::string>& att_names){};
void modify_edge_slot(std::uint64_t from, std::uint64_t to,  const std::string &type){};
void modify_edge_attrs_slot(std::uint64_t from, std::uint64_t to, const std::string &type, const std::vector<std::string>& att_names){};
void del_edge_slot(std::uint64_t from, std::uint64_t to, const std::string &edge_tag){};
void del_node_slot(std::uint64_t from){};     
"""

class specificworker_h(TemplateDict):
    def __init__(self, component):
        super(specificworker_h, self).__init__()
        self.component = component

        self['dsr_slots'] = self.dsr_slots()

    def dsr_slots(self):
        result = ""
        if self.component.dsr:
            result = DSR_SLOTS
        return result

