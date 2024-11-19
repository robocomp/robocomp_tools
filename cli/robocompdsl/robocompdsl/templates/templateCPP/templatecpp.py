import os

from robocompdsl.templates.common.abstracttemplatesmanager import ComponentTemplatesManager
from robocompdsl.templates.common.plugin_collection import PluginCollection
from robocompdsl.templates.templateCPP import plugins

FILE_PATH = os.path.dirname(os.path.realpath(__file__))


class TemplatesManagerCpp(ComponentTemplatesManager):
    def __init__(self, component):
        self.files = {
            'regular': [
                'CMakeLists.txt', 'DoxyFile', 'README-RCNODE.txt', 'README.md', 'etc/config', 'generated/main.cpp',
                'generated/CMakeLists.txt', 'src/CMakeLists.txt',
                'generated/genericworker.h', 'generated/genericworker.cpp', 'src/specificworker.h',
                'src/specificworker.cpp', 'src/mainUI.ui'
            ],
            'avoid_overwrite': [
                'src/specificworker.h', 'src/specificworker.cpp', 'src/CMakeLists.txt',
                'src/mainUI.ui', 'README.md','etc/config'
            ],
            'servant_files': ["SERVANT.H", "SERVANT.CPP"],
            'template_path': "templateCPP/files/"
        }
        current_plugins = PluginCollection(plugins.__name__)
        super(TemplatesManagerCpp, self).__init__(component, current_plugins)





