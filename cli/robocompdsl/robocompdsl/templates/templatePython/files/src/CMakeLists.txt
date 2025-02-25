cmake_minimum_required(VERSION 2.6)
PROJECT(  ${component_name} )

IF ( "$$ENV{ROBOCOMP}" STREQUAL "")
  MESSAGE(WARNING "ROBOCOMP variable not set. Using the default value: /home/robocomp/robocomp")
  SET (ENV{ROBOCOMP} "/home/robocomp/robocomp/")
ENDIF ( "$$ENV{ROBOCOMP}" STREQUAL "")

IF(NOT EXISTS $$ENV{ROBOCOMP}/cmake)
  MESSAGE(FATAL_ERROR "Couldn't find RoboComp in $$ENV{ROBOCOMP}! Exiting...")
ENDIF(NOT EXISTS $$ENV{ROBOCOMP}/cmake)

INCLUDE( $$ENV{ROBOCOMP}/cmake/robocomp.cmake )

ROBOCOMP_IDSL_TO_ICE( CommonBehavior ${ifaces_list} )
