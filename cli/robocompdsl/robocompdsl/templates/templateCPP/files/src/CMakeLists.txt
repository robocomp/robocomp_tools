# Use the latest policy behavior
cmake_policy(VERSION 3.10)

# Set the minimum version
cmake_minimum_required(VERSION 3.10)

# Project call
project(${component_name})

# Check for ROBOCOMP environment variable
if (DEFINED ENV{ROBOCOMP})
  set(ROBOCOMP_WORKSPACE $$ENV{ROBOCOMP})
else()
  message(WARNING "ROBOCOMP environment variable not set. Using the default value: /opt/robocomp")
  set(ROBOCOMP_WORKSPACE "/opt/robocomp/")
endif()

# Check for RoboComp's existence
if(NOT EXISTS $${ROBOCOMP_WORKSPACE}/cmake)
  message(FATAL_ERROR "Couldn't find RoboComp in $${ROBOCOMP_WORKSPACE}! Exiting...")
endif()

# Include RoboComp and Qt cmake scripts
list(APPEND CMAKE_MODULE_PATH $${ROBOCOMP_WORKSPACE}/cmake)
include(robocomp)
include(modules/qt)

# Include the specific cmake list
include(CMakeListsSpecific.txt)

# Sources set
set(SOURCES
    $${SOURCES}
    $${ROBOCOMP_WORKSPACE}/classes/rapplication/rapplication.cpp
    $${ROBOCOMP_WORKSPACE}/classes/sigwatch/sigwatch.cpp
    main.cpp
    genericmonitor.cpp
    commonbehaviorI.cpp
    genericworker.cpp
    ${interface_sources}
    ${statemachine_visual_sources}
)

add_library(${component_name}_lib STATIC ${SOURCES})
target_include_directories(${component_name}_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

${cpp11_ice_packages}

${agm_includes}

# RoboComp initialize
ROBOCOMP_INITIALIZE( $${ROBOCOMP_WORKSPACE}/ )
${wrap_ice}

${wrap_ui}

# Specify construction and link process
add_executable(${component_name} $${SOURCES} $${MOC_SOURCES} $${RC_SOURCES} $${UI_HEADERS})

# Link libraries
target_link_libraries(${component_name}
    $${LIBS}
    $${STATIC_LIBS}
    $${SPECIFIC_LIBS}
    $${QT_LIBRARIES}
    $${Ice_LIBRARIES}
)

# Add compile options
# no-char8_t to avoid a problem with ICE Connection lib.
target_compile_options(${component_name} PRIVATE -g  -fmax-errors=1 -fno-char8_t)
set_target_properties(${component_name} PROPERTIES
    CXX_STANDARD 20
)

# Installation
install(TARGETS ${component_name} DESTINATION $${RC_COMPONENT_INSTALL_PATH}/bin
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE
)