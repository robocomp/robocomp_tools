from robocompdsl.templates.common.templatedict import TemplateDict

GUI_INCLUDE_STR = """
#if Qt5_FOUND
	#include <QtWidgets>
#else
	#include <QtGui>
#endif
#include <ui_mainUI.h>
"""


class genericworker_h(TemplateDict):

    def __init__(self, component):
        super(genericworker_h, self).__init__()
        self.component = component
        self['gui_includes'] = self.gui_includes()


    def gui_includes(self):
        result = ""
        if self.component.gui is not None:
            result += GUI_INCLUDE_STR
        return result
