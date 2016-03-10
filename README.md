#Chloride Site Generator 2
The spiritual successor to the original abdomination.

##Building
CSG2 depends on a few Python libraries, and runs on Python 3.
To build, you also need a version of CMake newer than 3.0.
To install, run the following:

    pip3 install -r requirements.txt
    mkdir build && cd build

The next part depends on if you'll install it with `make install` or a package manager.

###Manual
Run the following:

    cmake -DCMAKE_INSTALL_PREFIX:STRING=/opt/csg2 ..
    make
    make install

###Packaging
Assuming `$pkgdir` is the package root, run the following:

    cmake -DCMAKE_INSTALL_PREFIX:STRING=/usr ..
    make
    make DESTDIR=${pkgdir} install

##Post install
CSG2 runs as nobody:nogroup by default, and pulls sites from `/srv/csg2/`. Make sure it is readable. The nginx frontend requires `/var/log/csg2/` to exist.
