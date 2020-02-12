export NS3_TAG ?= 3.30
COHYDRA_TAG ?= $(shell if [ -z "`git status --porcelain`" ]; then git rev-parse --short HEAD; else echo dirty; fi)
export COHYDRA_TAG := ${COHYDRA_TAG}

docker_build := docker build --build-arg NS3_TAG --build-arg COHYDRA_TAG

.PHONY: latest ns-3 cohydra-base cohydra cohydra-dev docs

all: ns-3 cohydra-base cohydra cohydra-dev
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
	docker tag osmhpi/ns-3:${NS3_TAG} osmhpi/ns-3:latest
	docker tag osmhpi/cohydra:base-${COHYDRA_TAG} osmhpi/cohydra:base
	docker tag osmhpi/cohydra:${COHYDRA_TAG} osmhpi/cohydra:latest
	docker tag osmhpi/cohydra:dev-${COHYDRA_TAG} osmhpi/cohydra:dev

ns-3:
	${docker_build} -t osmhpi/ns-3:${NS3_TAG} container-images/ns-3

cohydra-base:
	${docker_build} -t osmhpi/cohydra:base-${COHYDRA_TAG} container-images/cohydra-base

cohydra:
	${docker_build} -t osmhpi/cohydra:${COHYDRA_TAG} .

cohydra-dev:
	${docker_build} -t osmhpi/cohydra:dev-${COHYDRA_TAG} container-images/cohydra-dev

save: git-is-clean
	docker save \
		osmhpi/ns-3:${NS3_TAG} \
		osmhpi/ns-3:latest \
		osmhpi/cohydra:base-${COHYDRA_TAG} \
		osmhpi/cohydra:base \
		osmhpi/cohydra:${COHYDRA_TAG} \
		osmhpi/cohydra:latest \
		osmhpi/cohydra:dev-${COHYDRA_TAG} \
		osmhpi/cohydra:dev

docs:
	$(MAKE) -C docs
