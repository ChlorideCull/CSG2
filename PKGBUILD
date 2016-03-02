# This is an example PKGBUILD file. Use this as a start to creating your own,
# and remove these comments. For more information, see 'man PKGBUILD'.
# NOTE: Please fill out the license field for your package! If it is unknown,
# then please put 'unknown'.

# Maintainer: Sebastian Johansson <steamruler@gmail.com>
pkgname=CSG2-git
pkgver=2.0
pkgrel=1
epoch=
pkgdesc="Python-based CMS"
arch=(any)
url="https://github.com/ChlorideCull/CSG2"
license=('GFDL' 'AGPL' 'MIT')
groups=()
depends=('python')
makedepends=('cmake')
checkdepends=()
optdepends=()
provides=('CSG2')
conflicts=('CSG2')
replaces=()
backup=()
options=()
install=
changelog=
source=("git+https://github.com/ChlorideCull/CSG2.git")
noextract=()
md5sums=('SKIP')
validpgpkeys=()

build() {
	cd "CSG2"
	mkdir build && cd build
	cmake -DCMAKE_INSTALL_PREFIX:STRING=/usr ..
	make
}

package() {
	cd "CSG2"
	cd build
	make DESTDIR="$pkgdir/" install
	mkdir -p "$pkgdir/srv/csg2"
	cp -r ../site.example "$pkgdir/srv/csg2/"
}
