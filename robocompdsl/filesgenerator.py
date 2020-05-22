import filecmp
import os
import subprocess
import sys

import robocompdslutils
from templates.templateCPP.templatecpp import TemplatesManagerCpp
from templates.templateICE.templateice import TemplateManagerIce
from templates.templatePython.templatepython import TemplatesManagerPython

sys.path.append("/opt/robocomp/python")
from dsl_parsers import dsl_factory

LANG_TO_TEMPLATE = {
    'cpp': 'cpp',
    'cpp11': 'cpp',
    'python': 'python',
    'python3': 'python',
    'python2': 'python'
}

class FilesGenerator:
    def __init__(self):
        self.__dsl_file = None
        self.__output_path = None
        self.__include_dirs = None
        self.diff = None
        self.ast = None

    @property
    def dsl_file(self):
        return self.__dsl_file

    @dsl_file.setter
    def dsl_file(self, value):
        assert isinstance(value, str), "dsl_file must be a string not %s" % str(type(value))
        assert os.path.exists(value), "%s cdsl file not found." % value
        self.__dsl_file = value

    @property
    def output_path(self):
        return self.__output_path

    @output_path.setter
    def output_path(self, value):
        assert isinstance(value, str), "output_path must be a string not %s" % str(type(value))
        self.__output_path = value

    @property
    def include_dirs(self):
        return self.__include_dirs

    @include_dirs.setter
    def include_dirs(self, value):
        assert isinstance(value, list), "include_dirs must be a string not %s" % str(type(value))
        self.__include_dirs = value

    def generate(self, input_file, output_path, include_dirs, diff=None):
        self.dsl_file = input_file
        self.output_path = output_path
        self.include_dirs = include_dirs
        self.diff = diff
        self.__load_ast()
        new_existing_files = self.__create_files()
        self.__show_diff(new_existing_files)

    def __load_ast(self):
        self.ast = dsl_factory.DSLFactory().from_file(self.dsl_file, includeDirectories=self.include_dirs)

    def __create_files(self):
        new_existing_files = {}
        if self.dsl_file.endswith(".cdsl") or self.dsl_file.endswith(".jcdsl"):
            # Check output directory
            self.__create_component_directories()

            # Generate specific_component
            new_existing_files = self.__generate_component()

            if self.ast.usingROS is True:
                for imp in self.ast.imports:
                    self.generate_ROS_headers(imp)
        elif self.dsl_file.endswith(".idsl"):
            new_existing_files = self.__generate_interface()
        return new_existing_files

    def __show_diff(self, new_existing_files):
        # Code to launch diff tool on .new files to be compared with their old version
        if self.diff is not None and len(new_existing_files) > 0:
            diff_tool, _ = robocompdslutils.get_diff_tool(prefered=self.diff)
            print("Executing diff tool for existing files. Close if no change is needed.")
            for o_file, n_file in new_existing_files.items():
                if not filecmp.cmp(o_file, n_file):
                    print([diff_tool, o_file, n_file])
                    try:
                        subprocess.call([diff_tool, o_file, n_file])
                    except KeyboardInterrupt:
                        print("Comparision interrupted. All files have been generated. Check this .new files manually:")
                        for o_file2, n_file2 in new_existing_files.items():
                            if not filecmp.cmp(o_file2, n_file2):
                                print("%s %s" % (o_file2, n_file2))
                        break
                    except Exception as e:
                        print("Exception trying to execute %s" % diff_tool)
                        print(e.message)

                else:
                    print("Binary equal files %s and %s" % (o_file, n_file))

    def __generate_component(self):
        language = self.ast.language.lower()

        template = LANG_TO_TEMPLATE[language]
        # TODO: Template objects could be moved to a TemplateFactory
        if template == 'python':
            template_obj = TemplatesManagerPython(self.ast)
        else:
            template_obj = TemplatesManagerCpp(self.ast)
        new_existing_files = template_obj.generate_files(self.output_path)
        # for module in self.ast.idsl_pool.modulePool.values():
        #     template_obj = TemplateManagerIce(module)
        #     ice_directory = os.path.join(self.output_path, "ice_files")
        #     ice_new_existing_files = template_obj.generate_files(ice_directory)
        #     new_existing_files.update(ice_new_existing_files)
        return new_existing_files

    def __generate_interface(self):
        template_obj = TemplateManagerIce(self.ast)
        new_existing_files = template_obj.generate_files(self.output_path)
        return new_existing_files

    def __create_component_directories(self):
        if not os.path.exists(self.output_path):
            robocompdslutils.create_directory(self.output_path)

        # Create directories within the output directory
        new_dirs = ["bin", "src", "etc"]
        for new_dir in new_dirs:
            if self.ast.language.lower() == "python" and new_dir == "bin": continue
            robocompdslutils.create_directory(os.path.join(self.output_path, new_dir))

        # TODO: Probably deprecated. Check.
    def generate_ROS_headers(self, idsl_file):
        """
        :param idsl_file: is the IDSL file imported in the CDSL
        :return:
        """
        imported = []
        idsl = dsl_factory.DSLFactory().from_file(idsl_file, includeDirectories=self.include_dirs)
        if not os.path.exists(self.output_path):
            robocompdslutils.create_directory(self.output_path)

        def generarH(idslFile, imported):
            idsl = dsl_factory.DSLFactory().from_file(idslFile)
            try:
                os.system("rm -f " + self.output_path + "/" + idsl['module']['name'] + "ROS/msg/__init__.py")
                os.system("rm -f " + self.output_path + "/" + idsl['module']['name'] + "ROS/srv/__init__.py")
            except KeyError:
                print("No module found in %s" % idsl_file)
            for imp in idsl['structs'] + idsl['sequences']:
                if imp['type'] in ['struct', 'sequence']:
                    for f in ["SERVANT.MSG"]:
                        ofile = self.output_path + "/" + imp['name'] + "." + f.split('.')[-1].lower()
                        print('Generating', ofile, ' (servant for', idslFile.split('.')[0].lower() + ')')

                        ofile_dir = os.path.dirname(ofile)
                        if not os.path.exists(ofile_dir):
                            os.makedirs(ofile_dir)
                        # Call cog
                        params = {
                            "theIDSLPaths": '#'.join(self.include_dirs),
                            "structName": imp['name'],
                            "theIDSL": idslFile
                        }
                        cog_command = robocompdslutils.generate_cog_command(params,
                                                                            "/opt/robocomp/share/robocompdsl/templateCPP/" + f,
                                                                            ofile)
                        robocompdslutils.run_cog_and_replace_tags(cog_command, ofile)
                        commandCPP = "/opt/ros/melodic/lib/gencpp/gen_cpp.py " + ofile + " -Istd_msgs:/opt/ros/melodic/share/std_msgs/msg -I" + \
                                     idsl['name'] + "ROS:" + self.output_path
                        commandPY = "/opt/ros/melodic/lib/genpy/genmsg_py.py " + ofile + " -Istd_msgs:/opt/ros/melodic/share/std_msgs/msg -I" + \
                                    idsl['name'] + "ROS:" + self.output_path
                        for impo in imported:
                            if not impo == idsl['module']['name'] + "ROS":
                                commandCPP = commandCPP + " -I" + impo + ":" + self.output_path
                                commandPY = commandPY + " -I" + impo + ":" + self.output_path
                        commandCPP = commandCPP + " -p " + idsl['name'] + "ROS -o " + self.output_path + "/" + idsl[
                            'name'] + "ROS -e /opt/ros/melodic/share/gencpp"
                        commandPY = commandPY + " -p " + idsl['name'] + "ROS -o " + self.output_path + "/" + idsl[
                            'name'] + "ROS/msg"
                        if self.ast.language.lower() == 'cpp':
                            os.system(commandCPP)
                        else:
                            os.system(commandPY)
                        try:
                            fileInit = open(self.output_path + "/" + idsl['name'] + "ROS/msg/__init__.py", 'a')
                            fileInit.write("from ._" + imp['name'] + " import *\n")
                            fileInit.close()
                        except:
                            pass
            for imp in idsl['interfaces']:
                for ima in [self.ast.implements + self.ast.requires]:
                    im = ima
                    if type(im) != type(''):
                        im = im[0]
                    if not communication_is_ice(ima) and im == imp['name']:
                        for method in imp['methods'].values():
                            if 'params' in method:
                                if len(method['params']) == 2:
                                    for f in ["SERVANT.SRV"]:
                                        ofile = self.output_path + "/" + method['name'] + "." + f.split('.')[
                                            -1].lower()
                                        print('Generating', ofile, ' (servant for',
                                              idslFile.split('.')[0].lower() + ')')
                                        # Call cog
                                        params = {
                                            "theIDSLPaths": '#'.join(self.include_dirs),
                                            "methodName": method['name'],
                                            "theIDSL": idslFile
                                        }
                                        cog_command = robocompdslutils.generate_cog_command(params,
                                                                                            "/opt/robocomp/share/robocompdsl/templateCPP/" + f,
                                                                                            ofile)
                                        robocompdslutils.run_cog_and_replace_tags(cog_command, ofile)
                                        commandCPP = "/opt/ros/melodic/lib/gencpp/gen_cpp.py " + ofile + " -Istd_msgs:/opt/ros/melodic/share/std_msgs/msg -Istd_srvs:/opt/ros/melodic/share/std_srv/cmake/../srv -I" + \
                                                     idsl['module']['name'] + "ROS:" + self.output_path
                                        commandPY = "/opt/ros/melodic/lib/genpy/gensrv_py.py " + ofile + " -Istd_msgs:/opt/ros/melodic/share/std_msgs/msg -Istd_srvs:/opt/ros/kinetic/share/std_srv/cmake/../srv -I" + \
                                                    idsl['module']['name'] + "ROS:" + self.output_path
                                        for impo in imported:
                                            if not impo == idsl['module']['name'] + "ROS":
                                                commandCPP = commandCPP + " -I" + impo + ":" + self.output_path
                                                commandPY = commandPY + " -I" + impo + ":" + self.output_path

                                        commandCPP = commandCPP + " -p " + idsl['module'][
                                            'name'] + "ROS -o " + self.output_path + "/" + idsl['module'][
                                                         'name'] + "ROS -e /opt/ros/melodic/share/gencpp/cmake/.."
                                        commandPY = commandPY + " -p " + idsl['module'][
                                            'name'] + "ROS -o " + self.output_path + "/" + idsl['module'][
                                                        'name'] + "ROS/srv"
                                        if self.ast.language.lower() == 'cpp':
                                            os.system(commandCPP)
                                        else:
                                            os.system(commandPY)
                                        try:
                                            fileInit = open(
                                                self.output_path + "/" + idsl['module'][
                                                    'name'] + "ROS/srv/__init__.py", 'a')
                                            fileInit.write("from ._" + method['name'] + " import *\n")
                                            fileInit.close()
                                        except:
                                            pass
                                else:
                                    for param in enumerate(method['params']):
                                        print(param[0], '-->', param[1])
                                    raise IndexError(
                                        "ERROR: ROS service with incorrect number of parameters. ROS only supports remote procedure calls of the form: void method(type inVar, out type outVar);")
                            else:
                                raise KeyError(
                                    "ERROR: service without params. Form is: void method(type inVar, out type outVar);")

            os.system("touch " + self.output_path + "/" + idsl['module']['name'] + "ROS/__init__.py")
            return idsl['module']['name'] + "ROS"

        try:
            for importIDSL in idsl['imports'] + idsl['recursive_imports']:
                imported.append(generarH("/opt/robocomp/interfaces/IDSLs/" + importIDSL, []))
        except:
            pass

        generarH(idsl_file, imported)
        os.system("rm " + self.output_path + "/*.msg")
        os.system("rm " + self.output_path + "/*.srv")

