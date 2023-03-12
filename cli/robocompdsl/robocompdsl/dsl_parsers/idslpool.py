import os
from collections import OrderedDict
from pathlib import Path
from typing import Optional, List

import pyparsing

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice
from robocompdsl.dsl_parsers.dsl_factory import DSLFactory
from robocompdsl.logger import logger


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
        self.include_directories = []
        self.update_directories(self.common_idsl_dirs + self.idsl_dir_in_env())

    def update_directories(self, directories: List) -> List:
        if any(not isinstance(d, Path) for d in directories):
            raise TypeError(f"Directories must be a list of Path objects. {directories} given")
        self.include_directories = list(set(directories + self.include_directories))
        logger.debug(f"Updated directories with {directories}: {self.include_directories}")
        return self.include_directories

    def idsl_dir_in_env(self) -> List:
        result = list(map(Path, os.getenv('ROBOCOMP_INTERFACES', '').split(':')))
        logger.debug(f"ROBOCOMP_INTERFACES: {os.getenv('ROBOCOMP_INTERFACES', '')} => {result}")
        return result

    @classmethod
    def get_comidsl_dirs(cls):
        return cls.common_idsl_dirs

    def add_idsl(self, filename: str) -> None:
        logger.debug(f"Adding idsl {filename} to the pool")
        module_name = filename.split('.')[0]
        if module_name not in self:
            for p in self.include_directories:
                try:
                    path = p / filename
                    logger.debug(f"Trying with {path}")

                    # if found, load the module from the file
                    module = DSLFactory().from_file(path)
                    # store the module
                    self[module_name] = module
                    # try to add the modules that this one imports
                    aux_imports = []
                    for i_import in module.imports:
                        if i_import != '' and i_import not in self:
                            if communication_is_ice(i_import):
                                aux_imports.append(i_import)
                    self.update_with_idsls(aux_imports)
                    return module
                except IOError as e:
                    logger.debug(f"File {filename} not found in {p} with error {e}")
                    pass
            if module_name not in self:
                raise ValueError('Couldn\'t locate %s ' % filename)
            logger.debug(f"Tryied to add {filename} to the pool but not found in {self.include_directories}")

        else:
            return self[module_name]

    def update_with_idsls(self, files: List[str]):
        """
        Recursively add the already loaded idsl modules to the pool.

        :param files: list of idsl files to be included in the pool (file.idsl)
        """
        if len(files) == 0:
            return []
        logger.debug(f"Looking for {files} in {self.include_directories}")
        recursive_imports = []
        for f in files:
            module_name = f.split('.')[0]
            if f not in self:
                module = self.add_idsl(f)
                for i_import in module.imports:
                    if i_import != '' and i_import not in self:
                        if communication_is_ice(i_import):
                            recursive_imports.append(i_import)
        return recursive_imports


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
        self._initialice_mandatory_modules()
        logger.debug(f"Looking for {interface} in {list(self.keys())}")
        for module_name in self:
            logger.debug(f"Module {module_name} has {len(self[module_name].interfaces)} interfaces")
            for m in self[module_name].interfaces:
                if m.name == interface:
                    logger.debug(f"Found {interface} in {module_name} ({self[module_name].filename}")
                    return self[module_name]
        logger.warning(f"Couldn't find any module providing {interface}")
        return None

    def module_inteface_check(self):
        for module in self:
            problem_found = True
            for m in self[module].interfaces:
                if m.name == os.path.splitext(os.path.basename(self[module]['filename']))[0]:
                    problem_found = False
                    break
            if problem_found:
                interface_names = []
                for m in self[module].interfaces:
                    interface_names.append(m.name)
                logger.warning(f"It's expected to find at least one interface with the name of the file."
                               f"\n\tExpected interface name <{os.path.splitext(os.path.basename(self[module]['filename']))[0]}> but only found "
                               f"<{', '.join(interface_names)}> in {self[module]['filename']}", style='red')

    def interfaces(self):
        """
        :return: a list of all the interfaces defined inside the modules
        """
        interfaces = []
        for module in self:
            for m in self[module].interfaces:
                interfaces.append(m.name)
        return interfaces

    def idsl_path(self, idsl_name):
        assert isinstance(idsl_name, str), "idsl_name parameter must be a string"
        if idsl_name.endswith('.idsl'):
            idsl_name = idsl_name[:-5]

        try:
            filepath = self[idsl_name]['filename']
            if filepath.is_file():
                return filepath
            else:
                logger.error(f"Weird, {filepath} is not a file")
        except KeyError:
            logger.debug(f"Couldn't find {idsl_name} in the pool")
        return None

    # Delayed initialization of the pool
    def __getitem__(self, item):
        if len(self) == 0:
            self._initialice_mandatory_modules()
        return super().__getitem__(item)

    def _initialice_mandatory_modules(self):
        if len(self) == 0:
            logger.debug(f"Initializing IDSLPool with {self.mandatory_idsls}")
            self.update_with_idsls(self.mandatory_idsls)
            self.module_inteface_check()
            logger.debug(f"IDSLPool initialized. Found {len(self)} modules.")
        else:
            logger.debug("IDSLPool already initialized.")


"""
This is a pythonic way to create a singleton class of IDSLPool
It's created on the first import of this module and then it's used everywhere.
"""
idsl_pool = IDSLPool()

