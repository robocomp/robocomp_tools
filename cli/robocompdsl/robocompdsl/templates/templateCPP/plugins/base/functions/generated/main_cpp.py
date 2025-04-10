import datetime
from string import Template

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils
from robocompdsl.templates.common.templatedict import TemplateDict

INCLUDE_STR = '#include <${iface_name}${suffix}.h>\n'


PROXY_PTR_STR = """${prx_type}Prx${ptr} ${lower}_proxy${num};\n"""


TOPIC_MANAGER_STR = """
IceStorm::TopicManagerPrx${ptr} topicManager;
try
{
	topicManager = ${type}(communicator()->stringToProxy(configLoader.get<std::string>("Proxies.TopicManager")));
	if (!topicManager)
	{
	    std::cout << "[" << PROGRAM_NAME << "]: TopicManager.Proxy not defined in config file."<<std::endl;
	    std::cout << "\t Config line example: TopicManager.Proxy=IceStorm/TopicManager:default -p 9999"<<std::endl;
        return EXIT_FAILURE;
	}
}
catch (const Ice::Exception &ex)
{
	std::cout << "[" << PROGRAM_NAME << "]: Exception: \'rcnode\' not running: " << ex << std::endl;
	return EXIT_FAILURE;
}
"""


PUBLISHES_STR = """
name_topic = configLoader.get<std::string>("Proxies.${name}Prefix${num}");

if (not name_topic.empty()){name_topic+="/";};
name_topic+="${name}";

std::cout << "[\\033[1;36m" << PROGRAM_NAME << "\\033[0m]: \\033[32mINFO\\033[0m Topic: " 
              << name_topic << " will be used for publication. \\033[0m\\n";

while (!${lower}_topic${num})
{
    try
    {
        ${lower}_topic${num} = topicManager->retrieve(name_topic);
    }
    catch (const IceStorm::NoSuchTopic&)
    {
        std::cout << "\\n\\n[\\033[1;36m" << PROGRAM_NAME << "\\033[0m]: \\033[1;33mWARNING\\033[0m " 
          << name_topic << " topic did not create. \\033[32mCreating...\\033[0m\\n\\n";
        try
        {
            ${lower}_topic${num} = topicManager->create(name_topic);

        }
        catch (const IceStorm::TopicExists&){
            // Another client created the topic.
            std::cout << "[\\033[31m" << PROGRAM_NAME << "\\033[0m]: \\033[1;33mWARNING\\033[0m publishing the " << name_topic << " topic. It's possible that other component have created\\n";
        }
    }
    catch(const IceUtil::NullHandleException&)
    {
        std::cout << "[\\033[31m" << PROGRAM_NAME << "\\033[0m]: \\033[31mERROR\\033[0m TopicManager is Null. Check that your configuration file contains an entry like:\\n"
          << "\\t\\t\\033[34mTopicManager.Proxy=IceStorm/TopicManager:default -p <port>\\033[0m\\n";
        return EXIT_FAILURE;
    }
}
"""

SUBSCRIBESTO_STR = """
// Server adapter creation and publication
${typetopic} ${lower}_topic${num};
${typeproxy} ${proxyname};
try
{
    tmp = configLoader.get<std::string>("Endpoints.${name}Topic${num}");
    name_topic = configLoader.get<std::string>("Endpoints.${name}Prefix${num}");

    if (not name_topic.empty()){name_topic+="/";};
    name_topic+="${name}";

    Ice::ObjectAdapterPtr ${name}_adapter${num} = communicator()->createObjectAdapterWithEndpoints(name_topic, tmp);
    ${ptr_type}Ptr ${lower}I_${num} = std::make_shared <${name}I>(worker, ${id});
    auto ${proxyname} = ${name}_adapter${num}->addWithUUID(${lower}I_${num})->ice_oneway();

    std::cout << "[\\033[1;36m" << PROGRAM_NAME << "\\033[0m]: \\033[32mINFO\\033[0m Topic: " 
              << name_topic << " will be used in subscription. \\033[0m\\n";

    if(!${lower}_topic${num})
    {
        try {
            ${lower}_topic${num} = topicManager->create(name_topic);
            std::cout << "\\n\\n[\\033[1;36m" << PROGRAM_NAME << "\\033[0m]: \\033[1;33mWARNING\\033[0m " 
              << name_topic << " topic did not create. \\033[32mTopic created\\033[0m\\n\\n";
        }
        catch (const IceStorm::TopicExists&) {
            //Another client created the topic
            try{
                std::cout << "[\\033[31m" << PROGRAM_NAME << "\\033[0m]: \\033[1;33mWARNING\\033[0m Probably other client already opened the topic. \\033[32mTrying to connect.\\033[0m\\n";
                ${lower}_topic${num} = topicManager->retrieve(name_topic);
            }
            catch(const IceStorm::NoSuchTopic&)
            {
                std::cout << "[" << PROGRAM_NAME << "]: Topic doesn't exists and couldn't be created.\\n";
                //Error. Topic does not exist
            }
        }
        catch(const IceUtil::NullHandleException&)
        {
            std::cout << "[\\033[31m" << PROGRAM_NAME << "\\033[0m]: \\033[31mERROR\\033[0m TopicManager is Null. Check that your configuration file contains an entry like:\\n"
              << "\\t\\t\\033[34mTopicManager.Proxy=IceStorm/TopicManager:default -p <port>\\033[0m\\n";
            return EXIT_FAILURE;
        }
        IceStorm::QoS qos;
        ${lower}_topic${num}->subscribeAndGetPublisher(qos, ${proxyname});
    }
    ${name}_adapter${num}->activate();
}
catch(const IceStorm::NoSuchTopic&)
{
    std::cout << "[" << PROGRAM_NAME << "]: Error creating ${name} topic.\\n";
    //Error. Topic does not exist
}
"""

IMPLEMENTS_STR = """
try
{
    // Server adapter creation and publication
    tmp = configLoader.get<std::string>("Endpoints.${name}${num}");
    Ice::ObjectAdapterPtr adapter${name}${num} = communicator()->createObjectAdapterWithEndpoints("${name}${num}", tmp);
    ${cpp_version}
    adapter${name}${num}->add(${lower}${num}, Ice::stringToIdentity("${lower}"));
    adapter${name}${num}->activate();
    std::cout << "[" << PROGRAM_NAME << "]: ${name} adapter created in port " << tmp << std::endl;
}
catch (const IceStorm::TopicExists&){
    std::cout << "[" << PROGRAM_NAME << "]: ERROR creating or activating adapter for ${name}\\n";
}
"""


REQUIRE_STR = """
try
{
    proxy = configLoader.get<std::string>("Proxies.${name}${proxynumber}");
    ${cpp_version}
}
catch(const Ice::Exception& ex)
{
    std::cout << "[" << PROGRAM_NAME << "]: Exception creating proxy ${name}${proxynumber}: " << ex;
    return EXIT_FAILURE;
}
qInfo("${name}Proxy${proxynumber} initialized Ok!");

"""

UNSUBSCRIBE_STR = """
try
{
	std::cout << \"Unsubscribing topic: ${name} \" <<std::endl;
	${name}_topic->unsubscribe( ${name} );
}
catch(const Ice::Exception& ex)
{
	std::cout << \"ERROR Unsubscribing topic: $name \" << ex.what()<<std::endl;
}
"""


class generated_main_cpp(TemplateDict):
    def __init__(self, component):
        super(generated_main_cpp, self).__init__()
        self.component = component
        self['year'] = str(datetime.date.today().year)
        self['component_name'] = component.name
        self['implements_interface_includes'] = self.interface_includes(self.component.implements, 'I', True)
        self['subscribes_interface_includes'] = self.interface_includes(self.component.subscribesTo, 'I', True)
        self['imports_interface_includes'] = self.interface_includes(self.component.recursiveImports)
        self['interface_includes'] = self.interface_includes(self.component.recursiveImports)
        self['proxies_map_creation'] = self.proxies_map_creation()
        self['publishes_proxy_ptr'] = self.proxy_ptr(self.component.publishes, 'pub')
        self['requires'] = self.requires()
        self['requires_proxy_ptr'] = self.proxy_ptr(self.component.requires)
        self['topic_manager_creation'] = self.topic_manager_creation()
        self['publish'] = self.publish()
        self['specificworker_creation'] = self.specificworker_creation()
        self['implements'] = self.implements()
        self['subscribes_to'] = self.subscribes_to()
        self['unsubscribe_code'] = self.unsubscribe_code()

    @staticmethod
    def interface_includes(interfaces, suffix='', lower=False):
        result = ""
        if interfaces is not None:
            interface_names = set()
            for interface in sorted(interfaces):
                if communication_is_ice(interface):
                    name = interface if isinstance(interface, str) else interface.name
                    name = name.split('/')[-1].split('.')[0]
                    if lower:
                        name = name.lower()
                    if name not in interface_names: 
                        interface_names.add(name)
                        result += Template(INCLUDE_STR).substitute(iface_name=name, suffix=suffix)
        return result

    def proxy_ptr(self, interfaces, prefix=''):
        result = ""
        for interface, num in get_name_number(interfaces):
            if communication_is_ice(interface):
                ptr = "Ptr"
                name = interface.name
                module = self.component.idsl_pool.module_providing_interface(name)
                proxy_type = utils.get_type_string(name, module['name'])
                result += Template(PROXY_PTR_STR).substitute(prx_type=proxy_type, ptr=ptr, lower=name.lower(), num=num,
                                                             prefix=prefix)
        return result

    def topic_manager_creation(self):
        result = "\n//Topic Manager code"
        need_topic = False
        for pub in self.component.publishes:
            if communication_is_ice(pub):
                need_topic = True
        for pub in self.component.subscribesTo:
            if communication_is_ice(pub):
                need_topic = True
        if need_topic:
            ptr = "Ptr"
            manager_type = "Ice::checkedCast<IceStorm::TopicManagerPrx>"
            result += Template(TOPIC_MANAGER_STR).substitute(ptr=ptr, type=manager_type)
        return result

    def publish(self):
        result = "\n//Publish code\n"
        for pba, num in get_name_number(self.component.publishes):
            if type(pba) == str:
                pb = pba
            else:
                pb = pba[0]
            if communication_is_ice(pba):
                result += f"std::shared_ptr<IceStorm::TopicPrx> {pb.lower()}_topic{num};\n"
                result += Template(PUBLISHES_STR).substitute(name=pb, lower=pb.lower(), num=num)
                module = self.component.idsl_pool.module_providing_interface(pb)
                result += f"auto {pb.lower()}{num} = {pb.lower()}_topic{num}->getPublisher()->ice_oneway();\n"
                result += f"{pb.lower()}_proxy{num} = Ice::uncheckedCast<RoboComp{pb}::{pb}Prx>({pb.lower()}{num});\n\n"
        return result

    def subscribes_to(self):
        result = "\n//Subscribe code"
        for interface, num in get_name_number(self.component.subscribesTo):
            name = interface.name
            if communication_is_ice(interface):
                typeTopic = "std::shared_ptr<IceStorm::TopicPrx>"
                typeProxy = "Ice::ObjectPrxPtr"

                module = self.component.idsl_pool.module_providing_interface(name)
                proxy_type = utils.get_type_string(name, module['name'])
                result += Template(SUBSCRIBESTO_STR).substitute(name=name, lower=name.lower(), typetopic=typeTopic, typeproxy=typeProxy,
                                                               proxyname= f"{name.lower()}{num}", ptr_type=proxy_type, num=num, id=num if num!="" else "0")
        return result

    def implements(self):
        result = "\n//Implement code"
        for ima, num in get_name_number(self.component.implements):
            if type(ima) == str:
                im = ima
            else:
                im = ima[0]
            if communication_is_ice(ima):
                cpp = f"auto {im.lower()}{num} = std::make_shared<{im}I>(worker, {num if num!="" else "0"});"
                result += Template(IMPLEMENTS_STR).substitute(name=im, lower=im.lower(), cpp_version=cpp, num=num)
        return result

    def requires(self):
        result = "\n//Require code"
        for interface, num in get_name_number(self.component.requires):
            name = interface.name
            if communication_is_ice(interface):
                module = self.component.idsl_pool.module_providing_interface(name)
                proxy_type = utils.get_type_string(name, module['name'])
                cpp = f"{name.lower()}_proxy{num} = Ice::uncheckedCast<{proxy_type}Prx>(communicator()->stringToProxy(proxy));"
                result += Template(REQUIRE_STR).substitute(name=name, lower=name.lower(), cpp_version=cpp, proxynumber=num)
        return result

    def specificworker_creation(self):
        result = ""
        var_name = 't'
        proxy_list = [interface.name.lower() + "_proxy" + num  for interface, num in get_name_number(self.component.requires)]
        proxy_list += [interface.name.lower() + "_proxy" + num for interface, num in get_name_number(self.component.publishes)]
        if proxy_list:
            result += "tprx = std::make_tuple(" + ",".join(proxy_list) + ");\n"
        else:
            result += "tprx = std::tuple<>();\n"
        result += "SpecificWorker *worker = new SpecificWorker(this->configLoader, {}prx, startup_check_flag);\n".format(var_name)
        return result

    def unsubscribe_code(self):
        result = "\n"
        for interface in self.component.subscribesTo:
            if communication_is_ice(interface):
                result = Template(UNSUBSCRIBE_STR).substitute(name=interface.name.lower())
        return result

    def proxies_map_creation(self):
        result = ""
        result += "TuplePrx tprx;\n"
        return result
