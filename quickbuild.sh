#!/bin/sh
mkdir -p build
rm -rf build
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX:STRING=/usr ..
make
cat>description-pak<<EOF
CSG2 is a decent-ish Python 3 powered CMS.
EOF
sudo checkinstall \
	--pkgname=csg2-git \
	--pkgversion=$(date +%Y%m%d) \
	--pkglicense=AGPL \
	--pkggroup=web \
	--nodoc

