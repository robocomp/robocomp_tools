from string import Template

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice, get_name_number
from robocompdsl.templates.common.templatedict import TemplateDict

STORM_TOPIC_MANAGER_STR = """\
# This property is used by the clients to connect to IceStorm.
Proxies.TopicManager = "IceStorm/TopicManager:default -p 9999"
"""

class etc_config(TemplateDict):
    def __init__(self, component):
        super(etc_config, self).__init__()
        self.component = component
        self['storm_topic_manager'] = self.storm_topic_manager()
        self['config_publishes_proxies'] = self.config_publishes_proxies()
        self['config_requires_proxies'] = self.config_requires_proxies()        
        self['config_subscribes_endpoints'] = self.config_subscribes_endpoints()
        self['config_implements_endpoints'] = self.config_implements_endpoints()

    def config_implements_endpoints(self):
        result = ""
        for interface, num in get_name_number(self.component.implements):
            if communication_is_ice(interface):
                result += f'Endpoints.{interface.name}{num} = "tcp -p 0"\n'
        if result != "":
            result = '# Endpoints for implements interfaces\n' + result
        return result

    def config_subscribes_endpoints(self):
        result = ""
        for interface, num in get_name_number(self.component.subscribesTo):
            if communication_is_ice(interface):
                result += f'Endpoints.{interface.name}Topic{num} = "tcp -p 0"\n'
                result += f'Endpoints.{interface.name}Prefix{num} = ""\n'
        if result != "":
            result = '# Endpoints for subscriptions interfaces\n' + result
        return result
    
    def config_publishes_proxies(self):
        result = ""
        for interface, num in get_name_number(self.component.publishes):
            if communication_is_ice(interface):
                result += f'Proxies.{interface.name}Prefix{num} = ""\n'
        if result != "":
            result = '# Proxies for publishes interfaces\n' + result
        return result

    def config_requires_proxies(self):
        result = ""
        for interface, num in get_name_number(self.component.requires):
            if communication_is_ice(interface):
                port = 0
                result += f'Proxies.{interface.name}{num} = "{interface.name.lower()}:tcp -h localhost -p {port}"\n'
                    
        if result != "":
            result = '# Proxies for required interfaces\n' + result
        return result

    def storm_topic_manager(self):
        result = ""
        if len(self.component.publishes + self.component.subscribesTo) > 0:
            result += STORM_TOPIC_MANAGER_STR
        return result

