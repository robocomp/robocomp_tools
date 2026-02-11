from robocompdsl.templates.common.templatedict import TemplateDict


class CMakeLists_txt(TemplateDict):
    def __init__(self, component):
        super(CMakeLists_txt, self).__init__()
        self.component = component
        self['component_name'] = self.component.name
        interface_names = []
        if self.component.imports is not None and self.component.imports is not None:
            for im in sorted(self.component.imports + self.component.ice_interfaces_names):
                name = im.split('/')[-1].split('.')[0]
                interface_names.append(name)
        self['ifaces_list'] = ' '.join(interface_names)

