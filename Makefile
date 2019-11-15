NS3_VERSION=3.29
NS3_DOWNLOAD=ns3/ns-${NS3_VERSION}.tar.bz2

init: install-ns3
	pip install -r requirements.txt

${NS3_DOWNLOAD}:
	mkdir -p ns3
	curl -sL -o $@ https://www.nsnam.org/releases/ns-allinone-${NS3_VERSION}.tar.bz2

install-ns3: ${NS3_DOWNLOAD}
	mkdir -p ns3 
	tar xvj --strip-components 1 -C ns3 -f ${NS3_DOWNLOAD}
	cd ns3 && ./build.py -- --prefix=./install
	cd ns3/ns-${NS3_VERSION} && ./waf install

.PHONY: init