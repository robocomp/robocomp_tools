import datetime
from string import Template

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils
from robocompdsl.templates.common.templatedict import TemplateDict


INTERFACE_TYPES_COMMENT_STR = """\
/**************************************/
// From the ${module_name} you can use this types:
${types}
"""

PROXY_METHODS_COMMENT_STR = """\
/**************************************/
// From the ${module_name} you can ${action} this methods:
${methods}
"""

class specificworker_cpp(TemplateDict):
    def __init__(self, component):
        super(specificworker_cpp, self).__init__()
        self.component = component
        self['year'] = str(datetime.date.today().year)
        self['proxy_map_type'] = self.proxy_map_type()
        self['proxy_map_name'] = self.proxy_map_name()
        self['implements'] = self.implements()
        self['subscribes'] = self.subscribes()
        self['interface_specific_comment'] = self.interface_specific_comment()

    def implements(self):
        result = ""
        pool = self.component.idsl_pool
        for impa, num in get_name_number(self.component.implements):
            if type(impa) == str:
                imp = impa
            else:
                imp = impa[0]
            module = pool.module_providing_interface(imp)
            for interface in module['interfaces']:
                if interface['name'] == imp:
                    for mname in interface['methods']:
                        method = interface['methods'][mname]
                        param_str_a = ''
                        body_code = ""
                        if communication_is_ice(impa):
                            param_str_a = utils.get_parameters_string(method, module['name'])
                            return_type = utils.get_type_string(method['return'], module['name'])
                            result += f"{return_type} SpecificWorker::{interface['name']}{num}_{method['name']}({param_str_a})\n{{\n"
                            if return_type != "void":
                                result += "\t"+return_type+" ret{};\n\t//implementCODE\n" + body_code + "\n\treturn ret;\n}\n\n"
                            else:
                                result += "\t//implementCODE\n" + body_code + "\n}\n\n"
                        else:
                            pass
        return result

    def subscribes(self):
        result = ""
        pool = self.component.idsl_pool
        for subscribes, num in get_name_number(self.component.subscribesTo):
            module = pool.module_providing_interface(subscribes.name)
            if module is None:
                raise ValueError('\nCan\'t find module providing %s\n' % subscribes.name)
            for interface in module['interfaces']:
                if interface['name'] == subscribes.name:
                    for mname in interface['methods']:
                        method = interface['methods'][mname]
                        param_str_a = ''
                        body_code = ""
                        if communication_is_ice(subscribes):
                            param_str_a = utils.get_parameters_string(method, module['name'])
                            result += f"//SUBSCRIPTION to {method['name']} method from {interface['name']} interface\n"
                            result += f"{method['return']} SpecificWorker::{interface['name']}{num}_{method['name']}({param_str_a})\n{{\n//subscribesToCODE\n" + body_code + "\n}\n\n"
                        else:
                            pass
        return result


    def proxy_map_type(self):
        return "TuplePrx"

    def proxy_map_name(self):
        return "tprx"

    def interface_specific_comment(self):
        result = ""
        interfaces_by_type = {
            "requires": self.component.requires,
            "publishes": self.component.publishes,
            "implements": self.component.implements,
            "subscribesTo": self.component.subscribesTo
        }
        for interface_type, interfaces in interfaces_by_type.items():
            for interface, num in get_name_number(interfaces):
                if communication_is_ice(interface):
                    proxy_methods_calls = ""
                    module = self.component.idsl_pool.module_providing_interface(interface.name)
                    if interface_type in ["publishes", "requires"]:
                        if interface_type == 'publishes':
                            action = "publish calling"
                            pub = "pub"
                        else:
                            action = "call"
                            pub = ""
                        proxy_reference = "this->" + interface.name.lower() + num + f"_{pub}proxy->"

                        for method_name, method_details in module['interfaces'][0]['methods'].items():
                            return_type = f"{module['name']}::{method_details['return']}"
                            method_signature = f"{return_type} {proxy_reference}{method_name}("
                            params = []
                            for param in method_details['params']:
                                param_type = param['type']
                                param_name = param['name']
                                params.append(f"{param_type} {param_name}")
                            method_signature += ", ".join(params) + ")"
                            proxy_methods_calls += f"// {method_signature}\n"

                        if proxy_methods_calls:
                            result += Template(PROXY_METHODS_COMMENT_STR).substitute(module_name=module['name'],
                                                                                     methods=proxy_methods_calls,
                                                                                     action=action)

                    structs_str = ""
                    for struct in module['structs']:
                        structs_str += f"// {struct['name'].replace('/', '::')}\n"
                    if structs_str:
                        result += Template(INTERFACE_TYPES_COMMENT_STR).substitute(module_name=module['name'],
                                                                                   types=structs_str)
        return result