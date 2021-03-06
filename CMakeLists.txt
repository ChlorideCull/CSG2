cmake_minimum_required(VERSION 3.0)
project(CSG2 NONE)
option(ENABLE_SYSTEMD "Generate a systemd service" ON)

set(POSTINSTALLPATH ${CMAKE_INSTALL_PREFIX})
set(SERVUSERNAME "mediacouriersrv")

install(FILES serve.py sandbox.py configman.py DESTINATION share/csg2)
install(DIRECTORY docs DESTINATION share/doc/csg2)
install(DIRECTORY themes DESTINATION share/csg2)
install(DIRECTORY default-files DESTINATION share/csg2)
install(DIRECTORY nginx-default DESTINATION share/csg2)
configure_file(nginx.conf.in nginx.conf @ONLY)
configure_file(site-template.conf.in site-template.conf @ONLY)
install(FILES ${CMAKE_BINARY_DIR}/nginx.conf ${CMAKE_BINARY_DIR}/site-template.conf DESTINATION share/csg2)
install(DIRECTORY site.example DESTINATION share/doc/csg2)

find_program(USERADDBIN useradd)
if(USERADDBIN-NOTFOUND)
    message(FATAL_ERROR "Failed to find useradd in the system path. Is the OS all right?")
endif()
configure_file(csg2.py.in csg2 @ONLY)
install(PROGRAMS ${CMAKE_BINARY_DIR}/csg2 DESTINATION bin)

if(ENABLE_SYSTEMD)
    find_program(NGINXBIN nginx) # If only every distro did the sane thing and
    find_program(KILLBIN kill)   # put everything in /usr/bin, sigh
    if(NGINXBIN-NOTFOUND)
        message(FATAL_ERROR "Failed to find nginx in the system path. Is it installed?")
    endif()
    if(KILLBIN-NOTFOUND)
        message(FATAL_ERROR "Failed to find kill in the system path, of all things. Is the OS all right?")
    endif()
    configure_file(csg2@.service.in csg2@.service @ONLY)
    configure_file(csg2-nginx.service.in csg2-nginx.service @ONLY)
    install(FILES ${CMAKE_BINARY_DIR}/csg2@.service ${CMAKE_BINARY_DIR}/csg2-nginx.service DESTINATION lib/systemd/system)
endif()
