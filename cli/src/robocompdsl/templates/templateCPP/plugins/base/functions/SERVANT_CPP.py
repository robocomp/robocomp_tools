from string import Template
import datetime

from robocompdsl.templates.common.templatedict import TemplateDict
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils


INTERFACE_METHOD_STR = """
${ret} ${interface_name}I::${method_name}(${input_params})
{
    if (!worker)
        throw std::runtime_error("Worker is null");
        
    #ifdef HIBERNATION_ENABLED
		worker->hibernationTick();
	#endif
    
	${to_return}${method_name}Handlers.at(id)(${param_str});
}
"""

class SERVANT_CPP(TemplateDict):
    def __init__(self, component, interface_name):
        super(SERVANT_CPP, self).__init__()
        self.component = component
        module = self.component.idsl_pool.module_providing_interface(interface_name)
        self['year'] = str(datetime.date.today().year)
        self["interfaces_number"] = self["interfaces_number"] =   sum(1 for sublist in self.component.implements if sublist[0] == interface_name) + \
                                                                sum(1 for sublist in self.component.subscribesTo if sublist[0] == interface_name)
        self['interface_name'] = interface_name
        self['interface_name_lower'] = interface_name.lower()
        self['interface_methods_creation'] = self.interface_methods_creation(interface_name)
        self['array_handlers_creation'] = self.array_handlers_creation(interface_name, self["interfaces_number"])


    def interface_methods_creation(self,  interface_name):
        result = ""
        pool = self.component.idsl_pool
        module = pool.module_providing_interface(interface_name)
        if module is None:
            return result
        for interface in module['interfaces']:
            if interface['name'] == interface_name:
                for mname in interface['methods']:
                    method = interface['methods'][mname]

                    ret = utils.get_type_string(method['return'], module['name'])
                    name = method['name']

                    param_str_a = utils.get_parameters_string(method, module['name'])
                    if param_str_a:
                        param_str_a = f"{param_str_a}, const Ice::Current&"
                    else:
                        param_str_a = "const Ice::Current&"
                    param_str_b = ''
                    for p in method['params']:
                        if param_str_b == '':
                            delim = ''
                        else:
                            delim = ', '
                        param_str_b += delim + p['name']

                    result += Template(INTERFACE_METHOD_STR).substitute(ret=ret,
                                                                        interface_name=interface['name'],
                                                                        method_name=name,
                                                                        input_params=param_str_a,
                                                                        to_return="return " if ret != "void" else "",
                                                                        param_str=param_str_b
                                                                        )
        return result
    
    def array_handlers_creation(self, interface_name, interfaces_number):
        result = ""
        pool = self.component.idsl_pool
        module = pool.module_providing_interface(interface_name)
        if module is None:
            return result

        for interface in module['interfaces']:
            if interface['name'] != interface_name:
                continue
            
            for mname, method in interface['methods'].items():
                ret = utils.get_type_string(method['return'], module['name'])
                to_return = True if ret != 'void' else False
                handler_block = f"{mname}Handlers = {{\n"

                for i in range(interfaces_number):
                    # Parámetros como: auto a, auto b, ...
                    param_names = []
                    for idx, p in enumerate(method['params']):
                        param_names.append(f"auto &{chr(97 + idx)}")  # a, b, c...

                    lambda_args = ", ".join(param_names)
                    call_args = ", ".join([p.split()[-1][1:] for p in param_names])  # solo a, b, c...

                    handler_block += f"\t[this]({lambda_args}){f' -> {ret}' if to_return else ''} {{if (worker != nullptr) {'return ' if to_return else ''}worker->{interface_name}{'' if i==0 else i}_{mname}({call_args}); else throw std::runtime_error(\"Worker is null\");}},\n"

                handler_block = handler_block.rstrip(",\n") + "\n};\n\n"
                result += handler_block

        return result
