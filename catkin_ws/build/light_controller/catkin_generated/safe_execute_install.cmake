execute_process(COMMAND "/home/njog/homeautomation/catkin_ws/build/light_controller/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/njog/homeautomation/catkin_ws/build/light_controller/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
