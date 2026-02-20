import datetime

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.common.templatedict import TemplateDict


DSR_INIT_STR = """\
agent_name = configData.get("Agent", {}).get("name")
agent_id = configData.get("Agent", {}).get("id")

# Initialize DSR
sur_names = ConfigLoader.get_sur_names(configData, "Agent")

self.graphs = {}
self.g = None
if not sur_names:
    domain = configData.get("Agent", {}).get("domain", 0)
    config_file = configData.get("Agent", {}).get("configFile")
    
    new_graph = DSRGraph(0, agent_name, agent_id, config_file, True, domain)
    self.g = new_graph
    
    print("Graph loaded")
    self.graphs[""] = self.g
else:
    print(f"Multiple graphs found: {len(sur_names)}")
    
    for name in sur_names:
        prefix_data = configData["Agent"][name]
        
        config_file = prefix_data.get("configFile")
        domain = prefix_data.get("domain", 0)

        self.graphs[name] = DSRGraph(0, agent_name, agent_id, config_file, True, domain)
        print(f"Graph {name} loaded")

    self.g = self.graphs[sur_names[0]]
"""


class src_genericworker_py(TemplateDict):
    def __init__(self, component):
        super(src_genericworker_py, self).__init__()
        self.component = component
        self['year'] = str(datetime.date.today().year)
        self['insert_dsr'] = self.insert_dsr()
        self['import_dsr'] = self.import_dsr()



    def import_dsr(self):
        if self.component.dsr:
            return "from pydsr import DSRGraph\nfrom ConfigLoader import ConfigLoader"
        else:
            return ""

    def insert_dsr(self):
        if self.component.dsr:
            return DSR_INIT_STR
        else:
            return ""