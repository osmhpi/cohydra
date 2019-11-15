NS3_VERSION=3.29
NS3_DOWNLOAD=ns3/ns-${NS3_VERSION}.tar.bz2

init: install-ns3
	pip install -r requirements.txt

install-dependencies:
	sudo apt update
	sudo apt upgrade gcc g++ python python-dev mercurial bzr gdb\
		valgrind gsl-bin libgsl-dev libgsl-dbg libgsl-dev flex bison tcpdump\
		sqlite sqlite3 libsqlite3-dev libxml2 libxml2-dev libgtk2.0-0 libgtk2.0-dev\
		uncrustify doxygen graphviz imagemagick python-pygraphviz python-kiwi\
		libgoocanvas-2.0-dev python-pygccxml cmake autoconf libc6-dev libc6-dev-i386\
		g++-multilib texlive texlive-extra-utils texlive-latex-extra texlive-font-utils dvipng git\
		ipython libboost-signals-dev libboost-filesystem-dev openmpi-bin openmpi-common openmpi-doc\
		libopenmpi-dev qt4-default libqt4-dev unzip p7zip-full unrar-free\
		mercurial net-tools bridge-utils uml-utilities 

${NS3_DOWNLOAD}:
	mkdir -p ns3
	curl -sL -o $@ https://www.nsnam.org/releases/ns-allinone-${NS3_VERSION}.tar.bz2

install-ns3: install-dependencies ${NS3_DOWNLOAD}
	mkdir -p ns3 
	tar xvj --strip-components 1 -C ns3 -f ${NS3_DOWNLOAD}
	cd ns3 && ./build.py -- --prefix=./install
	cd ns3/ns-${NS3_VERSION} && ./waf install

.PHONY: init install-dependencies