# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The program to use to edit the cache.
CMAKE_EDIT_COMMAND = /usr/bin/cmake-gui

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/h20/robocomp/tools/rcmanager

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/h20/robocomp/tools/rcmanager

# Include any dependencies generated for this target.
include CMakeFiles/rcmanager.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/rcmanager.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/rcmanager.dir/flags.make

CMakeFiles/rcmanager.dir/rcmanager.c.o: CMakeFiles/rcmanager.dir/flags.make
CMakeFiles/rcmanager.dir/rcmanager.c.o: rcmanager.c
	$(CMAKE_COMMAND) -E cmake_progress_report /home/h20/robocomp/tools/rcmanager/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building C object CMakeFiles/rcmanager.dir/rcmanager.c.o"
	/usr/bin/cc  $(C_DEFINES) $(C_FLAGS) -o CMakeFiles/rcmanager.dir/rcmanager.c.o   -c /home/h20/robocomp/tools/rcmanager/rcmanager.c

CMakeFiles/rcmanager.dir/rcmanager.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/rcmanager.dir/rcmanager.c.i"
	/usr/bin/cc  $(C_DEFINES) $(C_FLAGS) -E /home/h20/robocomp/tools/rcmanager/rcmanager.c > CMakeFiles/rcmanager.dir/rcmanager.c.i

CMakeFiles/rcmanager.dir/rcmanager.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/rcmanager.dir/rcmanager.c.s"
	/usr/bin/cc  $(C_DEFINES) $(C_FLAGS) -S /home/h20/robocomp/tools/rcmanager/rcmanager.c -o CMakeFiles/rcmanager.dir/rcmanager.c.s

CMakeFiles/rcmanager.dir/rcmanager.c.o.requires:
.PHONY : CMakeFiles/rcmanager.dir/rcmanager.c.o.requires

CMakeFiles/rcmanager.dir/rcmanager.c.o.provides: CMakeFiles/rcmanager.dir/rcmanager.c.o.requires
	$(MAKE) -f CMakeFiles/rcmanager.dir/build.make CMakeFiles/rcmanager.dir/rcmanager.c.o.provides.build
.PHONY : CMakeFiles/rcmanager.dir/rcmanager.c.o.provides

CMakeFiles/rcmanager.dir/rcmanager.c.o.provides.build: CMakeFiles/rcmanager.dir/rcmanager.c.o

# Object files for target rcmanager
rcmanager_OBJECTS = \
"CMakeFiles/rcmanager.dir/rcmanager.c.o"

# External object files for target rcmanager
rcmanager_EXTERNAL_OBJECTS =

rcmanager: CMakeFiles/rcmanager.dir/rcmanager.c.o
rcmanager: CMakeFiles/rcmanager.dir/build.make
rcmanager: CMakeFiles/rcmanager.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking C executable rcmanager"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/rcmanager.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/rcmanager.dir/build: rcmanager
.PHONY : CMakeFiles/rcmanager.dir/build

CMakeFiles/rcmanager.dir/requires: CMakeFiles/rcmanager.dir/rcmanager.c.o.requires
.PHONY : CMakeFiles/rcmanager.dir/requires

CMakeFiles/rcmanager.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/rcmanager.dir/cmake_clean.cmake
.PHONY : CMakeFiles/rcmanager.dir/clean

CMakeFiles/rcmanager.dir/depend:
	cd /home/h20/robocomp/tools/rcmanager && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/h20/robocomp/tools/rcmanager /home/h20/robocomp/tools/rcmanager /home/h20/robocomp/tools/rcmanager /home/h20/robocomp/tools/rcmanager /home/h20/robocomp/tools/rcmanager/CMakeFiles/rcmanager.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/rcmanager.dir/depend

