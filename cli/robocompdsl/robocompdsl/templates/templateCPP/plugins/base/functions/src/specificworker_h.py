import datetime

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils
from robocompdsl.templates.common.templatedict import TemplateDict



STATEMACHINE_METHODS = r"""
/**
 * \brief Initializes the worker one time.
 */
void initialize();

/**
 * \brief Main compute loop of the worker.
 */
void compute();

/**
 * \brief Handles the emergency state loop.
 */
void emergency();

/**
 * \brief Restores the component from an emergency state.
 */
void restore();
"""

class specificworker_h(TemplateDict):
    def __init__(self, component):
        super(specificworker_h, self).__init__()
        self.component = component
        self['year'] = str(datetime.date.today().year)
        self['constructor_proxies'] = self.constructor_proxies()
        self['implements_method_definitions'] = self.implements_method_definitions()
        self['subscribes_method_definitions'] = self.subscribes_method_definitions()
        self['state_machine_method'] = self.state_machine_method()


    def generate_interface_method_definition(self, interface, num):
        result = ""
        pool = self.component.idsl_pool
        if type(interface) == str:
            interface_name = interface
        else:
            interface_name = interface.name
        module = pool.module_providing_interface(interface_name)
        for idsl_interface in module['interfaces']:
            if idsl_interface['name'] == interface_name:
                for method_name, method in idsl_interface['methods'].items():
                    if communication_is_ice(interface):
                        params_string = utils.get_parameters_string(method, module['name'])
                        return_type = utils.get_type_string(method['return'], module['name'])
                        result += f"{return_type} {idsl_interface['name']}{num}_{method['name']}({params_string});\n"
                    else:
                        pass
        return result

    def implements_method_definitions(self):
        result = ""
        for interface, num in get_name_number(self.component.implements):
            result += self.generate_interface_method_definition(interface, num)
        return result

    def subscribes_method_definitions(self):
        result = ""
        pool = self.component.idsl_pool
        for impa, num in get_name_number(self.component.subscribesTo):
            if type(impa) == str:
                imp = impa
            else:
                imp = impa.name
            module = pool.module_providing_interface(imp)
            for interface in module['interfaces']:
                if interface['name'] == imp:
                    for mname in interface['methods']:
                        method = interface['methods'][mname]
                        param_str_a = ''
                        if communication_is_ice(impa):
                            param_str_a = utils.get_parameters_string(method, module['name'])
                            return_type = utils.get_type_string(method['return'], module['name'])
                            result += f"{return_type} {interface['name']}{num}_{method['name']}({param_str_a});\n"
                        else:
                            pass
        return result

    def constructor_proxies(self):
        result = ""
        result += "TuplePrx tprx"
        return result

    def state_machine_method(self):
        result = STATEMACHINE_METHODS
        return result


