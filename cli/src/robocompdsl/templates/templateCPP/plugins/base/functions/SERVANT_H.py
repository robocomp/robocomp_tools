import datetime

from robocompdsl.templates.common.templatedict import TemplateDict
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils


class SERVANT_H(TemplateDict):
    def __init__(self, component, interface_name):
        super(SERVANT_H, self).__init__()
        self.component = component
        module = self.component.idsl_pool.module_providing_interface(interface_name)
        self['year'] = str(datetime.date.today().year)

        self["interfaces_number"] = self["interfaces_number"] =   sum(1 for sublist in self.component.implements if sublist[0] == interface_name) + \
                                                                sum(1 for sublist in self.component.subscribesTo if sublist[0] == interface_name)

        self['interface_name'] = interface_name
        self['interface_name_upper'] = interface_name.upper()
        self['filename_without_extension'] = module['filename'].split('/')[-1].split('.')[0]
        self['module_name'] = module['name']
        self['interface_methods_definition'] = self.interface_methods_definition(module,
                                                                                 interface_name)
        self['array_handlers_definition'] = self.array_handlers_definition(module, self["interfaces_number"])
        
        

    def interface_methods_definition(self, module, interface_name):
        result = ""
        for interface in module['interfaces']:
            if interface['name'] == interface_name:
                for mname in interface['methods']:
                    method = interface['methods'][mname]

                    ret = utils.get_type_string(method['return'], module['name'])
                    name = method['name']

                    param_str = utils.get_parameters_string(method, module['name'])
                    if param_str:
                        param_str = f"{param_str}, const Ice::Current&"
                    else:
                        param_str = "const Ice::Current&"
                    result += ret + ' ' + name + '(' + param_str + ');\n'
        return result
    
    def array_handlers_definition(self, module, interfaces_number):
        result = ""
        interface = next(i for i in module['interfaces'] if i['name'] == self['interface_name'])

        result += "// Array handlers for each method\n"

        for mname, method in interface['methods'].items():
            ret_type = utils.get_type_string(method['return'], module['name'])

            # Build parameter types only (without names)
            param_types = []
            for p in method['params']:
                type_str = utils.get_type_string(p['type'], module['name'])
                param_types.append(type_str)
            param_list = ", ".join(param_types)
            if param_list:
                param_list = f"{param_list}"
            else:
                param_list = "void"

            result += f"std::array<std::function<{ret_type}({param_list})>, {interfaces_number}> {mname}Handlers;\n"

        return result

