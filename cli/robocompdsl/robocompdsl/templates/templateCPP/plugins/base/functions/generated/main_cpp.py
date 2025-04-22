import datetime
from string import Template

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.templateCPP.plugins.base.functions import function_utils as utils
from robocompdsl.templates.common.templatedict import TemplateDict

INCLUDE_STR = '#include <${iface_name}${suffix}.h>\n'


PROXY_PTR_STR = """${prx_type}Prx${ptr} ${lower}_proxy${num};\n"""


REQUIRE_TEMPLATE_STR = """
template <typename ProxyType, typename ProxyPointer>
void require(const Ice::CommunicatorPtr& communicator,
             const std::string& proxyConfig, 
             const std::string& proxyName,
             ProxyPointer proxy)
{
    try
    {
        proxy = Ice::uncheckedCast<ProxyType>(communicator->stringToProxy(proxyConfig));
        std::cout << proxyName << " initialized Ok!\\n";
    }
    catch(const Ice::Exception& ex)
    {
        std::cout << "[" << PROGRAM_NAME << "]: Exception creating proxy " << proxyName << ": " << ex;
        throw;
    }
}
"""

IMPLMENTS_TEMPLATE_STR = """
template <typename InterfaceType>
void implement( const Ice::CommunicatorPtr& communicator,
                const std::string& endpointConfig,
                const std::string& adapterName,
                SpecificWorker* worker,
                int index)
{
    try
    {
        Ice::ObjectAdapterPtr adapter = communicator->createObjectAdapterWithEndpoints(adapterName, endpointConfig);
        auto servant = std::make_shared<InterfaceType>(worker, index);
        adapter->add(servant, Ice::stringToIdentity(adapterName));
        adapter->activate();
        std::cout << "[" << PROGRAM_NAME << "]: " << adapterName << " adapter created in port " << endpointConfig << std::endl;
    }
    catch (const IceStorm::TopicExists&)
    {
        std::cout << "[" << PROGRAM_NAME << "]: ERROR creating or activating adapter for " << adapterName << std::endl;
    }
}
"""

PUBLISH_TEMPLATE_STR = """
template <typename PubProxyType, typename PubProxyPointer>
void publish(const IceStorm::TopicManagerPrxPtr& topicManager,
             std::string name_topic,
             const std::string& topicBaseName,
             PubProxyPointer& pubProxy,
             const std::string& programName)
{
    if (!name_topic.empty()) name_topic += "/";
    name_topic += topicBaseName;

    std::cout << "[\\033[1;36m" << programName << "\\033[0m]: \\033[32mINFO\\033[0m Topic: " 
              << name_topic << " will be used for publication. \\033[0m\\n";

    std::shared_ptr<IceStorm::TopicPrx> topic;
    while (!topic)
    {
        try
        {
            topic = topicManager->retrieve(name_topic);
        }
        catch (const IceStorm::NoSuchTopic&)
        {
            std::cout << "\\n\\n[\\033[1;36m" << programName << "\\033[0m]: \\033[1;33mWARNING\\033[0m " 
                      << name_topic << " topic did not create. \\033[32mCreating...\\033[0m\\n\\n";
            try
            {
                topic = topicManager->create(name_topic);
            }
            catch (const IceStorm::TopicExists&)
            {
                std::cout << "[\\033[31m" << programName << "\\033[0m]: \\033[1;33mWARNING\\033[0m publishing the " 
                          << name_topic << " topic. It's possible that other component have created\\n";
            }
        }
        catch(const IceUtil::NullHandleException&)
        {
            std::cout << "[\\033[31m" << programName << "\\033[0m]: \\033[31mERROR\\033[0m TopicManager is Null.\\n";
            throw;
        }
    }
    auto publisher = topic->getPublisher()->ice_oneway();
    pubProxy = Ice::uncheckedCast<PubProxyType>(publisher);
}
"""


SUBCRIBE_TEMPLATE_STR = """
template <typename SubInterfaceType>
void subscribe( const Ice::CommunicatorPtr& communicator,
                const IceStorm::TopicManagerPrxPtr& topicManager,
                const std::string& endpointConfig,
                std::string name_topic,
                const std::string& topicBaseName,
                SpecificWorker* worker,
                int index,
                std::shared_ptr<IceStorm::TopicPrx> topic,
                Ice::ObjectPrxPtr& proxy, 
                const std::string& programName)
{
    try   
    {  
        if (!name_topic.empty()) name_topic += "/";
        name_topic += topicBaseName;

        Ice::ObjectAdapterPtr adapter = communicator->createObjectAdapterWithEndpoints(name_topic, endpointConfig);
        auto servant = std::make_shared<SubInterfaceType>(worker, index);
        auto proxy = adapter->addWithUUID(servant)->ice_oneway();

        std::cout << "[\\033[1;36m" << programName << "\\033[0m]: \\033[32mINFO\\033[0m Topic: " 
                  << name_topic << " will be used in subscription. \\033[0m\\n";

        std::shared_ptr<IceStorm::TopicPrx> topic;
        if(!topic)
        {
            try {
                topic = topicManager->create(name_topic);
                std::cout << "\\n\\n[\\033[1;36m" << programName << "\\033[0m]: \\033[1;33mWARNING\\033[0m " 
                          << name_topic << " topic did not create. \\033[32mTopic created\\033[0m\\n\\n";
            }
            catch (const IceStorm::TopicExists&) {
                try{
                    std::cout << "[\\033[31m" << programName << "\\033[0m]: \\033[1;33mWARNING\\033[0m Probably other client already opened the topic. \\033[32mTrying to connect.\\033[0m\\n";
                    topic = topicManager->retrieve(name_topic);
                }
                catch(const IceStorm::NoSuchTopic&)
                {
                    std::cout << "[" << programName << "]: Topic doesn't exists and couldn't be created.\\n";
                    return;
                }
            }
            catch(const IceUtil::NullHandleException&)
            {
                std::cout << "[\\033[31m" << programName << "\\033[0m]: \\033[31mERROR\\033[0m TopicManager is Null.\\n";
                throw;
            }
            IceStorm::QoS qos;
            topic->subscribeAndGetPublisher(qos, proxy);
        }
        adapter->activate();
    }
    catch(const IceStorm::NoSuchTopic&)
    {
        std::cout << "[" << PROGRAM_NAME << "]: Error creating topic.\\n";
    }
}
"""

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

UNSUBSCRIBE_STR = """
try
{
${unsubscribe}
}
catch(const Ice::Exception& ex)
{
	std::cout << \"ERROR Unsubscribing\" << ex.what()<<std::endl;
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
        self['add_templates'] = self.add_templates()

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
        if prefix == "pub":        
            for pba, num in get_name_number(self.component.publishes):
                if type(pba) == str:
                    name = pba
                else:
                    name = pba[0]
                if communication_is_ice(pba):
                    module = self.component.idsl_pool.module_providing_interface(name)
                    proxy_type = utils.get_type_string(name, module['name'])
                    result+=f'std::shared_ptr<IceStorm::TopicPrx> {name.lower()}_topic{num};\nIce::ObjectPrxPtr {name.lower()}{num};\n'
            result+='\n'

        return result

    def topic_manager_creation(self):
        result = "\n//Topic Manager code\n"
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
    

    #Todo
    def add_templates(self):
        result = ""
        if len(self.component.implements) > 0:
            result+=IMPLMENTS_TEMPLATE_STR
        if len(self.component.requires) > 0:
            result+=REQUIRE_TEMPLATE_STR
        if len(self.component.publishes) > 0:
            result+=PUBLISH_TEMPLATE_STR
        if len(self.component.subscribesTo) > 0:
            result+=SUBCRIBE_TEMPLATE_STR
        return result


    def publish(self):
        result = "\n//Publish code\n"
        for pba, num in get_name_number(self.component.publishes):
            if type(pba) == str:
                name = pba
            else:
                name = pba[0]
            if communication_is_ice(pba):
                module = self.component.idsl_pool.module_providing_interface(name)
                proxy_type = utils.get_type_string(name, module['name'])
                result += f'''publish<{proxy_type}Prx, {proxy_type}PrxPtr>(topicManager,
                    configLoader.get<std::string>("Proxies.{name}Prefix{num}"),
                    "{name}", {name.lower()}_proxy{num}, PROGRAM_NAME);\n'''

        return result

    def subscribes_to(self):
        result = "\n//Subscribe code\n"
        for interface, num in get_name_number(self.component.subscribesTo):
            name = interface.name
            if communication_is_ice(interface):                
                result += f'''subscribe<{name}I>(communicator(),
                    topicManager, configLoader.get<std::string>("Endpoints.{name}Topic{num}"),
				    configLoader.get<std::string>("Endpoints.{name}Prefix{num}"), "{name}", worker,  {num if num!="" else "0"},
				    {name.lower()}_topic, {name.lower()}, PROGRAM_NAME);\n'''
        return result

    def implements(self):
        result = "\n//Implement code\n"
        for ima, num in get_name_number(self.component.implements):
            if type(ima) == str:
                name = ima
            else:
                name = ima[0]
            if communication_is_ice(ima):
                result += f'''implement<{name}I>(communicator(),
                    configLoader.get<std::string>("Endpoints.{name}{num}"), 
                    "{name}{num}", worker,  {num if num!="" else "0"});\n'''

        return result

    def requires(self):
        result = "\n//Require code\n"
        for interface, num in get_name_number(self.component.requires):
            name = interface.name
            if communication_is_ice(interface):
                module = self.component.idsl_pool.module_providing_interface(name)
                proxy_type = utils.get_type_string(name, module['name'])
                result += f'''require<{proxy_type}Prx, {proxy_type}PrxPtr>(communicator(),
                    configLoader.get<std::string>("Proxies.{name}{num}"), "{name}Proxy{num}", {name.lower()}_proxy{num});\n'''
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
        unsubscribe = ""
        for interface, num in get_name_number(self.component.publishes):
            if communication_is_ice(interface):
                name = interface.name.lower()
                unsubscribe += f'\tstd::cout << \"Unsubscribing topic: {name}{num} " <<std::endl;\n\t{name}_topic{num}->unsubscribe({name}{num});\n'

                result = Template(UNSUBSCRIBE_STR).substitute(unsubscribe=unsubscribe)
        return result

    def proxies_map_creation(self):
        result = ""
        result += "TuplePrx tprx;\n"
        return result
