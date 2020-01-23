FROM debian:10 AS build

# ---------------- install ----------------
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
	bzip2 \
	cmake \
	curl \
	g++ \
	git \
	libclang-dev \
	llvm-dev \
	make \
	patch \
	python3-dev \
	python3-pip \
	python3-setuptools \
	python3-wheel \
	qt5-default \
	&& \
	apt-get autoremove -y && \
	apt-get clean -y && \
	rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=false

RUN pip3 install --no-cache-dir \
	cxxfilt \
	git+https://github.com/felix-gohla/pygccxml@v1.9.2 \
	&& true

# ---------------- CastXML ----------------
WORKDIR /opt/castxml
RUN git clone --branch v0.2.0 --depth 1 https://github.com/CastXML/CastXML.git . && \
	test "$(git rev-parse HEAD)" = 5ba47e3b67c4a9070e8404ed2db4d16c52e4267b && \
	cmake . && \
	make -j $(nproc) && \
	make install

# ---------------- download ----------------
ENV NS3_VERSION=3.30

# 3.29
# ENV NS3_DOWNLOAD_SHA1=8e712a744a07318d0416dbf85137d11635a02e9d

# 3.30
ENV NS3_DOWNLOAD_SHA1=b4d40bb9777ee644bdba50e3a2e221da85715b4e

WORKDIR /opt/ns-3
RUN curl -L -o ../ns-3.tar.bz2 https://www.nsnam.org/releases/ns-allinone-${NS3_VERSION}.tar.bz2 && \
	echo "${NS3_DOWNLOAD_SHA1} ../ns-3.tar.bz2" | sha1sum -c && \
	tar xj --strip-components 1 -f ../ns-3.tar.bz2 && \
	rm ../ns-3.tar.bz2

# ---------------- NetAnim ----------------
COPY netanim_python_${NS3_VERSION}.patch ..
RUN patch -p 1 -i ../netanim_python_${NS3_VERSION}.patch && \
	cd netanim-* && \
	qmake NetAnim.pro && \
	make -j $(nproc)

# ---------------- ns-3 ----------------
RUN cd ns-${NS3_VERSION} && \
	./waf configure && \
	./waf --apiscan=netanim && \
	cd .. && \
	./build.py -- install --destdir=/build && \
	cp netanim-*/NetAnim /build/usr/local/bin

################################################################################

FROM debian:10

# ---------------- install ----------------
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
	libpython3.7 \
	libqt5printsupport5 \
	python3 \
	&& \
	apt-get autoremove -y && \
	apt-get clean -y && \
	rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=false

# ---------------- copy ----------------
COPY --from=build /build /

# ---------------- setup ----------------
ENV PYTHONPATH=/usr/local/lib/python3/dist-packages
ENV LD_LIBRARY_PATH=/usr/local/lib
