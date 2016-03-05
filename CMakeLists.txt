cmake_minimum_required(VERSION 3.0)
project(CSG2 NONE)
option(ENABLE_SYSTEMD "Generate a systemd service" ON)

set(POSTINSTALLPATH ${CMAKE_INSTALL_PREFIX})

install(FILES serve.py sandbox.py DESTINATION share/csg2)
install(DIRECTORY docs DESTINATION share/doc/csg2)
install(DIRECTORY themes DESTINATION share/csg2)
configure_file(nginx.conf.in nginx.conf @ONLY)
install(FILES ${CMAKE_BINARY_DIR}/nginx.conf site-template.conf DESTINATION share/csg2)
install(DIRECTORY site.example DESTINATION share/doc/csg2)
configure_file(csg2.py.in csg2 @ONLY)
install(PROGRAMS ${CMAKE_BINARY_DIR}/csg2 DESTINATION bin)
if(ENABLE_SYSTEMD)
    execute_process(COMMAND which nginx OUTPUT_VARIABLE NGINXBIN OUTPUT_STRIP_TRAILING_WHITESPACE) # Thanks, Ubuntu, for putting nginx in /usr/sbin, because it's clearly the best option.
    execute_process(COMMAND which kill OUTPUT_VARIABLE KILLBIN OUTPUT_STRIP_TRAILING_WHITESPACE)   # Yet, you place kill in /bin.
    configure_file(csg2@.service.in csg2@.service @ONLY)
    configure_file(csg2-nginx.service.in csg2-nginx.service @ONLY)
    install(FILES ${CMAKE_BINARY_DIR}/csg2@.service ${CMAKE_BINARY_DIR}/csg2-nginx.service DESTINATION lib/systemd/system)
endif()
