from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice
from robocompdsl.templates.common.templatedict import TemplateDict

DSR_FIND_EIGEN = """\
find_package (Eigen3 3.3 REQUIRED NO_MODULE)
"""

DSR_LIBS = " dsr_core dsr_gui dsr_api fastcdr fastdds osgDB OpenThreads Eigen3::Eigen QGLViewer-qt6 Qt6OpenGLWidgets"


class generated_CMakeLists_txt(TemplateDict):
    def __init__(self, component):
        super(generated_CMakeLists_txt, self).__init__()
        dsr_find_eigen = ""
        dsr_libs = ""
        if component.dsr:
            dsr_find_eigen = DSR_FIND_EIGEN
            dsr_libs = DSR_LIBS
        self['dsr_find_eigen'] = dsr_find_eigen
        self['dsr_libs'] = dsr_libs
