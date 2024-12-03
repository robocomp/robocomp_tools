import datetime
from string import Template

import robocompdsl.dsl_parsers.parsing_utils as p_utils
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils
from robocompdsl.templates.common.templatedict import TemplateDict


INITIALIZE_METHOD_STR = """\
void SpecificWorker::initialize()
{
    std::cout << "initialize worker" << std::endl;
    //initializeCODE

    /////////GET PARAMS, OPEND DEVICES....////////
    //int period = configLoader.get<int>("Period.Compute") //NOTE: If you want get period of compute use getPeriod("compute")
    //std::string device = configLoader.get<std::string>("Device.name") 

}
"""

COMPUTE_METHOD_STR = """\
void SpecificWorker::compute()
{
    std::cout << "Compute worker" << std::endl;
	//computeCODE
	//try
	//{
	//  camera_proxy->getYImage(0,img, cState, bState);
    //    if (img.empty())
    //        emit goToEmergency()
	//  memcpy(image_gray.data, &img[0], m_width*m_height*sizeof(uchar));
	//  searchTags(image_gray);
	//}
	//catch(const Ice::Exception &e)
	//{
	//  std::cout << "Error reading from Camera" << e << std::endl;
	//}
}
"""

EMERGENCY_METHOD_STR = """\
void SpecificWorker::emergency()
{
    std::cout << "Emergency worker" << std::endl;
    //emergencyCODE
    //
    //if (SUCCESSFUL) //The componet is safe for continue
    //  emmit goToRestore()
}
"""

RESTORE_METHOD_STR = """\
//Execute one when exiting to emergencyState
void SpecificWorker::restore()
{
    std::cout << "Restore worker" << std::endl;
    //restoreCODE
    //Restore emergency component

}
"""

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
        self['initialize_method'] = self.initialize_method()
        self['compute_method'] = self.compute_method()
        self['emergency_method'] = self.emergency_method()
        self['restore_method'] = self.restore_method()
        self['implements'] = self.implements()
        self['subscribes'] = self.subscribes()
        self['interface_specific_comment'] = self.interface_specific_comment()


    def initialize_method(self):
        result = ""

        result += INITIALIZE_METHOD_STR
        return result

    def compute_method(self):
        result = ""
        result += COMPUTE_METHOD_STR
        return result
    
    def emergency_method(self):
        result = ""
        result += EMERGENCY_METHOD_STR
        return result
    
    def restore_method(self):
        result = ""
        result += RESTORE_METHOD_STR
        return result


    def implements(self):
        result = ""
        pool = self.component.idsl_pool
        for impa in self.component.implements:
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
                        if p_utils.communication_is_ice(impa):
                            param_str_a = utils.get_parameters_string(method, module['name'])
                            return_type = utils.get_type_string(method['return'], module['name'])
                            result += return_type + ' SpecificWorker::' + interface['name'] + "_" + method[
                                'name'] + '(' + param_str_a + ")\n{\n\t#ifdef HIBERNATION_ENABLED\n\t\thibernation = true;\n\t#endif\n"
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
        for subscribes in self.component.subscribesTo:
            module = pool.module_providing_interface(subscribes.name)
            if module is None:
                raise ValueError('\nCan\'t find module providing %s\n' % subscribes.name)
            for interface in module['interfaces']:
                if interface['name'] == subscribes.name:
                    for mname in interface['methods']:
                        method = interface['methods'][mname]
                        param_str_a = ''
                        body_code = ""
                        if p_utils.communication_is_ice(subscribes):
                            param_str_a = utils.get_parameters_string(method, module['name'])
                            result += "//SUBSCRIPTION to " + method['name'] + " method from " + interface[
                                'name'] + " interface\n"
                            result += method['return'] + ' SpecificWorker::' + interface['name'] + "_" + method[
                                'name'] + '(' + param_str_a + ")\n{\n#ifdef HIBERNATION_ENABLED\n\thibernation = true;\n#endif\n//subscribesToCODE\n" + body_code + "\n}\n\n"
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
            for interface, num in p_utils.get_name_number(interfaces):
                if p_utils.communication_is_ice(interface):
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