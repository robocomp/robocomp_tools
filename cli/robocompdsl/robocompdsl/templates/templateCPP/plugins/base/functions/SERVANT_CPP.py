from string import Template
import datetime

from robocompdsl.templates.common.templatedict import TemplateDict
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils


INTERFACE_METHOD_STR = """
${ret} ${interface_name}I::${method_name}(${input_params})
{

	if (id < ${method_name}Handlers.size())
		${to_return} ${method_name}Handlers[id](${param_str});
	else
		throw std::out_of_range("Invalid ${method_name} id: " + std::to_string(id));

	//${to_return}worker->${interface_name}_${method_name}(${param_str});
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
                handler_block = f"{mname}Handlers = {{\n"

                for i in range(interfaces_number):
                    # Parámetros como: auto a, auto b, ...
                    param_names = []
                    for idx, p in enumerate(method['params']):
                        param_names.append(f"auto {chr(97 + idx)}")  # a, b, c...

                    lambda_args = ", ".join(param_names)
                    call_args = ", ".join([p.split()[-1] for p in param_names])  # solo a, b, c...

                    handler_block += f"\t[this]({lambda_args}) {{ return worker->{interface_name}{'' if i==0 else i}_{mname}({call_args}); }},\n"

                handler_block = handler_block.rstrip(",\n") + "\n};\n\n"
                result += handler_block

        return result
