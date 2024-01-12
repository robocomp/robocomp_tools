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
        self['configure_statemachine'] = self.configure_statemachine()

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
            if self.component.language.lower() == 'cpp':
                if prx_type not in CPP_TYPES and '::' not in prx_type:
                    module = self.component.idsl_pool.module_providing_interface(name)
                    prx_type = f"{module['name']}::{prx_type}"
                result += name.lower() + num + proxy_suffix + " = (*(" + prx_type + "Prx*)mprx[\"" + name + name_suffix + num + "\"]);\n"
            else:
                result += name.lower() + num + proxy_suffix + " = std::get<" + str(cont) + ">(tprx);\n"
        return result


    def constructor_proxies(self):
        result = ""
        if self.component.language.lower() == 'cpp':
            result += "MapPrx& mprx"
        else:
            result += "TuplePrx tprx"
        return result

    def inherited_constructor(self):
        if self.component.gui:
            return "Ui_guiDlg()"
        else:
            return "QObject()"

    
    def state_statemachine(self):
        result = ""
        if self.component.statemachine_path is None:
            result += 'GRAFCETStep *stInt = new GRAFCETStep("Init", 0, nullptr, std::bind(&GenericWorker::initState, this));\n'
            result += 'stCompute = new GRAFCETStep("Compute", 100, std::bind(&GenericWorker::computeState, this));\n'
            result += 'GRAFCETStep *stEmergency = new GRAFCETStep("Emergency", 100, std::bind(&GenericWorker::emergencyState, this));\n'
            result += 'GRAFCETStep *stRestore = new GRAFCETStep("Restore", 0, nullptr, std::bind(&GenericWorker::restoreState, this));\n'
        return result
    
    def transition_statemachine(self):
        result = ""
        if self.component.statemachine_path is None:
            result += "stInt->addTransition(stInt, SIGNAL(entered()), stCompute);\n"
            result += "stCompute->addTransition(this, SIGNAL(goToEmergencyState()), stEmergency);\n"
            result += "stEmergency->addTransition(this, SIGNAL(goToRestoreState()), stRestore);\n"
            result += "stRestore->addTransition(stRestore, SIGNAL(entered()), stCompute);\n"
        return result
    
    def add_state_statemachine(self):
        result = ""
        if self.component.statemachine_path is None:
            result += "statemachine.addState(stInt);\n"
            result += "statemachine.addState(stCompute);\n"
            result += "statemachine.addState(stEmergency);\n"
            result += "statemachine.addState(stRestore);\n"
        return result

    def configure_statemachine(self):
        result = ""
        if self.component.statemachine_path is None:
            result += "statemachine.setChildMode(QState::ExclusiveStates);;\n"
            result += "statemachine.setInitialState(stInt);\n"
        return result