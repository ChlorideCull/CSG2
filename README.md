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

    cmake ..
    make
    make DESTDIR=/opt/csg2 install

###Packaging
Assuming `$pkgdir` is the package root, run the following:

    cmake -DREALPATH:STRING=/usr ..
    make
    make DESTDIR=${pkgdir}/usr install
