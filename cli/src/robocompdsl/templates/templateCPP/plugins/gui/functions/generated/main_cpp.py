from robocompdsl.templates.common.templatedict import TemplateDict



class generated_main_cpp(TemplateDict):

    def __init__(self, component):
        super(generated_main_cpp, self).__init__()
        self.component = component

        self['need_gui'] = self.need_gui()


    def need_gui(self):
        result = ""
        if self.component.gui is not None:
            result += "#define USE_QTGUI\n\n"
        else:
            result += "//#define USE_QTGUI\n\n"
        return result
