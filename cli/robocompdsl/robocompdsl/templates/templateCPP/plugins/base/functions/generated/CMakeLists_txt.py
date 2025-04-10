from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice
from robocompdsl.templates.common.templatedict import TemplateDict



class generated_CMakeLists_txt(TemplateDict):
    def __init__(self, component):
        super().__init__()
        self.component = component
        self['component_name'] = self.component.name
        self['interface_sources'] = self.interface_sources()
        self['wrap_ice'] = self.wrap_ice()

    def interface_sources(self):
        result = ""
        processed_interfaces = set()  
        
        for collection in [self.component.implements, self.component.subscribesTo]:
            for item in collection:
                im = item if isinstance(item, str) else item[0]
                if communication_is_ice(item):
                    interface_name = im.lower() + 'I.cpp'
                    if interface_name not in processed_interfaces:
                        result += interface_name + '\n'
                        processed_interfaces.add(interface_name)
        return result


    def wrap_ice(self):
        interface_names = set()
        
        if self.component.recursiveImports is not None and self.component.ice_interfaces_names is not None:
            for im in sorted(self.component.recursiveImports + self.component.ice_interfaces_names):
                name = im.split('/')[-1].split('.')[0]
                if name not in interface_names: interface_names.add(name)

        result = "ROBOCOMP_IDSL_TO_ICE("
        result += ' '.join(interface_names)
        result += ")\n"
        result += "ROBOCOMP_ICE_TO_SRC("
        result += ' '.join(interface_names)
        result += ")\n"

        return result

