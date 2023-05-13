cmake_minimum_required(VERSION 3.10)

# Preferably place project() call here, if you have one.
project(${component_name})

# Check for ROBOCOMP environment variable
if (DEFINED ENV{ROBOCOMP})
  set(ROBOCOMP_WORKSPACE $ENV{ROBOCOMP})
else()
  message(WARNING "ROBOCOMP environment variable not set. Using the default value: /opt/robocomp")
  set(ROBOCOMP_WORKSPACE "/opt/robocomp/")
endif()

# Check for RoboComp's existence
if(NOT EXISTS ${ROBOCOMP_WORKSPACE}/cmake)
  message(FATAL_ERROR "Couldn't find RoboComp in ${ROBOCOMP_WORKSPACE}! Exiting...")
endif()

# Include RoboComp and Qt cmake scripts
list(APPEND CMAKE_MODULE_PATH ${ROBOCOMP_WORKSPACE}/cmake)
include(robocomp)
include(qt)

# Include the specific cmake list
include(CMakeListsSpecific)

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


${cpp11_ice_packages}

${agm_includes}

# RoboComp initialize
ROBOCOMP_INITIALIZE( $${ROBOCOMP_WORKSPACE}/ )
${wrap_ice}
set(EXECUTABLE_OUTPUT_PATH $${RC_COMPONENT_DEVEL_PATH}/bin)

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

# Add compile definitions
# no-char8_t to avoid a problem with ICE Connection lib.
target_compile_definitions(${component_name} $${COMPONENT_COMPILE_DEFINITIONS} -g  -fmax-errors=1 -fno-char8_t)
set_target_properties(${component_name} PROPERTIES
    CXX_STANDARD 20
)

# Installation
install(TARGETS $${EXECUTABLE_OUTPUT_PATH}/${component_name} DESTINATION $${RC_COMPONENT_INSTALL_PATH}/bin
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE
)