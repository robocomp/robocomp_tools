import datetime
from string import Template
from robocompdsl.dsl_parsers.parsing_utils import get_name_number, communication_is_ice
from robocompdsl.templates.common.templatedict import TemplateDict


CPP_TYPES = ['int', 'float', 'bool', 'void']

class genericworker_cpp(TemplateDict):
    def __init__(self, component):
        super(genericworker_cpp, self).__init__()
        self.component = component
        self['year'] = str(datetime.date.today().year)
        self['constructor_proxies'] = self.constructor_proxies()
        self['inherited_constructor'] = self.inherited_constructor()
        self['require_and_publish_proxies_creation'] = self.require_and_publish_proxies_creation()
        self['state_statemachine'] = self.state_statemachine()        
        self['transition_statemachine'] = self.transition_statemachine()
        self['add_state_statemachine'] = self.add_state_statemachine()

    def require_and_publish_proxies_creation(self):
        result = ""
        cont = 0
        for interface, num in get_name_number(self.component.requires):
            result += self.get_proxy_string(interface, num, cont, is_publication=False)
            cont = cont + 1
        for interface, num in get_name_number(self.component.publishes):
            result += self.get_proxy_string(interface, num, cont, is_publication=True)
            cont = cont + 1
        return result

    def get_proxy_string(self, interface, num, cont, is_publication):
        result = ""
        if communication_is_ice(interface):
            name = interface.name
            prx_type = name
            if is_publication:
                proxy_suffix = "_pubproxy"
                name_suffix = "Pub"
            else:
                proxy_suffix = "_proxy"
                name_suffix = "Proxy"
            
            result += name.lower() + num + proxy_suffix + " = std::get<" + str(cont) + ">(tprx);\n"
        return result


    def constructor_proxies(self):
        result = ""
        result += "TuplePrx tprx"
        return result

    def inherited_constructor(self):
        if self.component.gui:
            return "Ui_guiDlg()"
        else:
            return "QObject()"

    def state_statemachine(self):
        result = ""

        result += 'states["Initialize"] = std::make_unique<GRAFCETStep>("Initialize", BASIC_PERIOD, nullptr, std::bind(&GenericWorker::initialize, this));\n'
        result += 'states["Compute"] = std::make_unique<GRAFCETStep>("Compute", configLoader.get<int>("Period.Compute"), std::bind(&GenericWorker::compute, this));\n'
        result += 'states["Emergency"] = std::make_unique<GRAFCETStep>("Emergency", configLoader.get<int>("Period.Emergency"), std::bind(&GenericWorker::emergency, this));\n'
        result += 'states["Restore"] = std::make_unique<GRAFCETStep>("Restore", BASIC_PERIOD, nullptr, std::bind(&GenericWorker::restore, this));\n'
        return result
    
    def transition_statemachine(self):
        result = ""
        result += 'states["Initialize"]->addTransition(states["Initialize"].get(), SIGNAL(entered()), states["Compute"].get());\n'
        result += 'states["Compute"]->addTransition(this, SIGNAL(goToEmergency()), states["Emergency"].get());\n'
        result += 'states["Emergency"]->addTransition(this, SIGNAL(goToRestore()), states["Restore"].get());\n'
        result += 'states["Restore"]->addTransition(states["Restore"].get(), SIGNAL(entered()), states["Compute"].get());\n'
        return result
    
    def add_state_statemachine(self):
        result = ""
        result += 'statemachine.addState(states["Initialize"].get());\n'
        result += 'statemachine.addState(states["Compute"].get());\n'
        result += 'statemachine.addState(states["Emergency"].get());\n'
        result += 'statemachine.addState(states["Restore"].get());\n'
        return result