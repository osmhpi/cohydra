export NS3_TAG ?= 3.30
export SUMO_TAG ?= 1.4.0
COHYDRA_TAG ?= $(shell if [ -z "`git status --porcelain`" ]; then git rev-parse --short HEAD; else echo dirty; fi)
export COHYDRA_TAG := ${COHYDRA_TAG}

docker_build := docker build --build-arg NS3_TAG --build-arg SUMO_TAG --build-arg COHYDRA_TAG

.PHONY: latest cohydra-base cohydra cohydra-dev docs

all: cohydra-base cohydra cohydra-dev
	#
	# build tag ${COHYDRA_TAG}
	#

git-is-clean:
ifeq '${shell git status --porcelain}' ''
	@ # git is clean
else
	${error Git status is not clean.}
endif


latest: git-is-clean all
	docker tag osmhpi/cohydra:base-${COHYDRA_TAG} osmhpi/cohydra:base
	docker tag osmhpi/cohydra:${COHYDRA_TAG} osmhpi/cohydra:latest
	docker tag osmhpi/cohydra:dev-${COHYDRA_TAG} osmhpi/cohydra:dev

cohydra-base:
	${docker_build} -t osmhpi/cohydra:base-${COHYDRA_TAG} docker/cohydra-base

cohydra:
	${docker_build} -t osmhpi/cohydra:${COHYDRA_TAG} . -f docker/Dockerfile

cohydra-dev:
	${docker_build} -t osmhpi/cohydra:dev-${COHYDRA_TAG} docker/cohydra-dev

pull-latest:
	docker pull osmhpi/cohydra:base
	docker pull osmhpi/cohydra:latest
	docker pull osmhpi/cohydra:dev

push:
	docker push osmhpi/cohydra:base-${COHYDRA_TAG}
	docker push osmhpi/cohydra:${COHYDRA_TAG}
	docker push osmhpi/cohydra:dev-${COHYDRA_TAG}

push-latest: git-is-clean push
	docker push osmhpi/cohydra:base
	docker push osmhpi/cohydra:latest
	docker push osmhpi/cohydra:dev

docs:
	$(MAKE) -C docs
