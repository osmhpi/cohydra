NS3_VERSION=3.29
NS3_DOWNLOAD=ns3/ns-${NS3_VERSION}.tar.bz2

shell:
	NS3_VERSION=${NS3_VERSION} pipenv shell

init: install-ns3
	pip install -r requirements.txt

install-dependencies:
	sudo apt update
	sudo apt upgrade gcc g++ g++-multilib pipenv mercurial bzr gdb\
		valgrind gsl-bin libgsl-dev libgsl-dbg libgsl-dev flex bison tcpdump\
		sqlite sqlite3 libsqlite3-dev libxml2 libxml2-dev libgtk2.0-0 libgtk2.0-dev\
		uncrustify doxygen graphviz libgraphviz-dev imagemagick\
		libgoocanvas-2.0-dev python-pygccxml cmake autoconf libc6-dev libc6-dev-i386\
		dvipng git ipython libboost-signals-dev libboost-filesystem-dev\
		openmpi-bin openmpi-common openmpi-doc\
		libopenmpi-dev qt4-default libqt4-dev unzip p7zip-full unrar-free\
		mercurial net-tools bridge-utils uml-utilities

${NS3_DOWNLOAD}:
	mkdir -p ns3
	curl -sL -o $@ https://www.nsnam.org/releases/ns-allinone-${NS3_VERSION}.tar.bz2

install-ns3: install-dependencies ${NS3_DOWNLOAD}
	mkdir -p ns3 
	tar xvj --strip-components 1 -C ns3 -f ${NS3_DOWNLOAD}
	cd ns3 && python3 ./build.py -- --prefix=${PWD}/ns3/ns-${NS3_VERSION}/install
	cd ns3/ns-${NS3_VERSION} && ./waf install

.PHONY: init install-dependencies shell