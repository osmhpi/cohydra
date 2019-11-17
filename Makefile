#### Variables
NS3_VERSION := 3.29
NS3_DOWNLOAD_SHA1 := 8e712a744a07318d0416dbf85137d11635a02e9d

#### Local variables
include Makefile.local

#### Default variables
NS3_BASE ?= ${CURDIR}/ns3

export NS3_HOME := ${NS3_BASE}/ns-${NS3_VERSION}
export PYTHONPATH := ${PYTHONPATH}:${NS3_BASE}/install/lib/python3.7/site-packages
export LD_LIBRARY_PATH := ${LD_LIBRARY_PATH}:${NS3_BASE}/install/lib
export PATH := ${PATH}:${NS3_BASE}/install/bin

PIPENV := ${shell which pipenv || echo /usr/bin/pipenv}
PIPENV_INSTALL := ${VIRTUAL_ENV}/.last-install
NS3_DOWNLOAD ?= ${NS3_HOME}.tar.bz2

#### Targets
.PHONY: shell env init pipenv clean uninstall-ns3

all: shell

.EXPORT_ALL_VARIABLES: shell

shell: ${PIPENV}
	@env -u MAKELEVEL pipenv shell || echo "Exit code: $$?"

env:
	env
	echo ${NS3_DOWNLOAD}
	echo ${CPP}

Makefile.local:
	touch $@

init: ${NS3_HOME}.installed ${PIPENV_INSTALL}

${PIPENV}:
	apt-get install pipenv

${PIPENV_INSTALL}: Pipfile | pipenv
	pipenv install
	touch $@

${NS3_HOME}.installed: ${NS3_DOWNLOAD} | pipenv
	mkdir -p ${NS3_BASE} 
	tar xvj --strip-components 1 -C ${NS3_BASE} -f ${NS3_DOWNLOAD}
	# Fix SuidBuild, see https://groups.google.com/forum/#!topic/ns-3-users/Wlaj57ehruM
	sed -i 's/"SuidBuild"/"SuidBuild_task"/' ${NS3_HOME}/wscript
	# build and install ns3
	cd $(NS3_BASE) && python3 ./build.py -- --enable-sudo --prefix=${NS3_BASE}/install
	cd ${NS3_HOME} && ./waf install
	touch $@

${NS3_DOWNLOAD}:
	mkdir -p ${dir ${NS3_DOWNLOAD}}
	curl -L -o $@ https://www.nsnam.org/releases/ns-allinone-${NS3_VERSION}.tar.bz2
	echo "${NS3_DOWNLOAD_SHA1} $@" | sha1sum -c 

ifeq "${VIRTUAL_ENV}" ""
pipenv:
	${info Run `make shell` first:}
	${info }
	${info   make shell}
	${info }
	${error Not in a pipenv envirenment}
else
pipenv:
endif

clean: uninstall-ns3

uninstall-ns3:
	${RM} -r ${NS3_BASE}
