import os
from collections import OrderedDict
from pathlib import Path
from typing import Optional, List

import pyparsing

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice
from src.robocomp.robocomp_tools.cli import logger


FILE_PATH_DIR = os.path.dirname(os.path.realpath(__file__))
ALT_INTERFACES_DIR = Path(FILE_PATH_DIR) / "../../../../../interfaces/IDSLs/"


class IDSLPool(OrderedDict):
    """
    This class is intended to load and store idsl modules from the corresponding files.
    idsl is the idsl filename or path
    module is the python structure loaded from an idsl file
    interfaces are the names defined for the communication inside idsl files and loaded in the modules.
    """
    mandatory_idsls = ["CommonBehavior.idsl"]

    common_idsl_dirs = [Path('/opt/robocomp/interfaces/IDSLs/'),
                             Path('~/robocomp/interfaces/IDSLs/').expanduser(),
                             ALT_INTERFACES_DIR]

    def __init__(self) -> None:
        super(IDSLPool, self).__init__()
        self.update_directories(self.common_idsl_dirs + self.idsl_dir_in_env())
        self.include_in_pool(self.mandatory_idsls)
        self.module_inteface_check()

    def update_directories(self, directories: List) -> List:
        if any(not isinstance(d, Path) for d in directories):
            raise TypeError(f"Directories must be a list of Path objects. {directories} given")
        self.include_directories = list(set(directories + self.include_directories))
        return self.include_directories

    def idsl_dir_in_env(self) -> List:
        return list(map(Path, os.getenv('ROBOCOMP_INTERFACES', '').split(':')))

    @classmethod
    def get_comidsl_dirs(cls):
        return cls.common_idsl_dirs

    def include_in_pool(self, files: List[str]):
        """
        Recursively add the already loaded idsl modules to the pool.

        :param files: list of idsl files to be included in the pool (file.idsl)
        """
        if len(files) == 0:
            return
        # for each file, look for it in the self.include_directories
        logger.debug(f"Looking for {files} in {self.include_directories}")
        for f in files:
            filename = f.split('.')[0]
            if filename not in self:
                for p in self.include_directories:
                    try:
                        path = p / f
                        logger.debug(f"Trying with {path}")

                        # WARN: import is here to avoid problem with recursive import on startup
                        from robocompdsl.dsl_parsers.dsl_factory import DSLFactory

                        # if found, load the module from the file
                        module = DSLFactory().from_file(str(path))
                        # store the module
                        self[filename] = module
                        # try to add the modules that this one imports
                        logger.debug(f"Calling include_in_pool with {module['imports'] + module['recursive_imports']}")
                        self.include_in_pool2(module['imports'] + module['recursive_imports'])
                        break
                    except IOError as e:
                        logger.debug(f"File {f} not found in {p} or {e}")
                        pass
                if filename not in self:
                    raise ValueError('Couldn\'t locate %s ' % f)

    def idsl_file_for_module(self, idsl_name):
        """
        Return the file path given the module object
        :param module: module to query on the pool for the related idsl file path
        :return: idsl file path
        """
        if idsl_name in self:
            return self[idsl_name]['filename']
        else:
            return None


    def module_providing_interface(self, interface):
        """
        Query the pool to get the module providing an interface
        :param interface: an interface to query the pool
        :return: the module providing the queried interface
        """
        for module in self:
            for m in self[module]['interfaces']:
                if m['name'] == interface:
                    return self[module]
        return None

    def module_inteface_check(self):
        for module in self:
            problem_found = True
            for m in self[module]['interfaces']:
                if m['name'] == os.path.splitext(os.path.basename(self[module]['filename']))[0]:
                    problem_found = False
                    break
            if problem_found:
                interface_names = []
                for m in self[module]['interfaces']:
                    interface_names.append(m['name'])
                logger.warning(f"It's expected to find at least one interface with the name of the file."
                               f"\n\tExpected interface name <{os.path.splitext(os.path.basename(self[module]['filename']))[0]}> but only found "
                               f"<{', '.join(interface_names)}> in {self[module]['filename']}", style='red')

    def interfaces(self):
        """
        :return: a list of all the interfaces defined inside the modules
        """
        interfaces = []
        for module in self:
            for m in self[module]['interfaces']:
                interfaces.append(m['name'])
        return interfaces

    def idsl_path(self, idsl_name):
        assert isinstance(idsl_name, str), "idsl_name parameter must be a string"
        if idsl_name.endswith('.idsl'):
            idsl_name = idsl_name[:-5]

        checked_paths = []
        filepath = self[idsl_name]['filename']
        if filepath is not None and filepath.is_file():
            return filepath
        else:
            logger.error(f"Couldn\'t locate {idsl_name} in any of the following paths: {checked_paths}")
        return None

    def generate_recursive_imports(self, initial_idsls):
        assert isinstance(initial_idsls, list), "initial_idsl, parameter must be a list, not %s" % str(type(initial_idsls))
        logger.debug(f"Generating recursive imports for {initial_idsls}")
        new_idsls = []
        for idsl_path in initial_idsls:
            idsl_basename = os.path.basename(idsl_path)
            logger.debug(f"Getting idsl file path for {idsl_basename} in {self.include_directories}")
            new_idsl_path = idsl_pool.idsl_path(idsl_basename, self.include_directories)
            logger.debug(f"\tTrying {idsl_basename} in {new_idsl_path}")
            from robocompdsl.dsl_parsers.dsl_factory import DSLFactory
            try:
                imported_module = DSLFactory().from_file(new_idsl_path)  # IDSLParsing.gimmeIDSL(attempt)
            except pyparsing.ParseException as e:
                logger.error(f"Parsing error in file {Text(new_idsl_path, style='red')} while generating recursive imports.")
                logger.error(f"Exception info: {Text(e.args[2], style='red')} in line {e.lineno} of:\n{Text(e.args[0].rstrip(), styled='magenta')}")
                raise
            except FileNotFoundError as e:
                logger.debug(f"File {Text(new_idsl_path, style='red')} not found while generating recursive imports.")
                continue
            logger.debug(f"\tFound {idsl_basename} in {new_idsl_path}")
            if imported_module is None:
                logger.warning(f"Couldn\'t locate {idsl_basename} in {new_idsl_path}")
                raise FileNotFoundError(f'Couldn\'t locate {idsl_basename} in {new_idsl_path}')

            # if importedModule['imports'] have a # at the end an emtpy '' is generated
            idsl_imports = imported_module['imports']
            logger.debug(f"\tImports found {idsl_imports}")
            # we remove all the '' ocurrences and existing imports
            aux_imports = []
            for i_import in idsl_imports:
                if i_import != '' and i_import not in initial_idsls:
                    if communication_is_ice(i_import):
                        aux_imports.append(i_import)
            idsl_imports = aux_imports
            logger.debug(f"\tImports after clean up {idsl_imports}")
            if len(idsl_imports) > 0 and idsl_imports[0] != '':
                new_idsls += idsl_imports + self.generate_recursive_imports(idsl_imports)
        logger.debug(f"Recursive imports found {new_idsls}")
        return list(set(new_idsls))

"""
This is a pythonic way to create a singleton class of IDSLPool
It's created on the first import of this module and then it's used everywhere.
"""
idsl_pool = IDSLPool([], [])

