import os
from collections import OrderedDict
from pathlib import Path
from typing import Optional, List

import pyparsing

from robocompdsl.dsl_parsers.parsing_utils import communication_is_ice
from robocompdsl.dsl_parsers.dsl_factory import DSLFactory
from robocompdsl.logger import logger
import collections



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
        """Add an IDSL file to the pool with proper dependency handling."""
        logger.debug(f"Adding idsl {filename} to the pool")
        module_name = filename.split('.')[0]
        
        if module_name in self:
            logger.debug(f"Module {module_name} already loaded")
            return self[module_name]
        
        # Try to find and load the file
        for p in self.include_directories:
            try:
                path = p / filename
                logger.debug(f"Trying with {path}")
                
                # Load the module
                module = DSLFactory().from_file(path)
                self[module_name] = module

                return module
                
            except IOError as e:
                logger.debug(f"File {filename} not found in {p}: {e}")
                continue
        
        raise ValueError(f'Could not locate {filename} in include directories')

    def update_with_idsls(self, files: List[str]) -> None:
        """Process multiple IDSL files with proper dependency resolution."""
        if not files:
            return
        
        logger.debug(f"Processing initial files: {files}")
        
        queue = collections.deque(files)
        processed = set()
        
        while queue:
            current_file = queue.popleft()
            
            if current_file in processed:
                continue
                
            processed.add(current_file)
            
            try:
                module = self.add_idsl(current_file)
                if module['imports'] is None:
                    continue
                # Add dependencies to the queue
                new_imports = [
                    imp for imp in module['imports']
                    if imp and communication_is_ice(imp)
                ]
                queue.extend(new_imports)
            except ValueError as e:
                logger.warning(f"Failed to process file {current_file}: {e}")
        return list(processed)

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
        for module in self:
            logger.debug(f"Module {module} has {len(self[module]['interfaces'])} interfaces")
            for m in self[module]['interfaces']:
                if m['name'] == interface:
                    logger.debug(f"Found {interface} in {module} ({self[module]['filename']}")
                    return self[module]
        logger.warning(f"Couldn't find any module providing {interface}")
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

