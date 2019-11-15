#!/bin/bash

# Install dependencies

sudo apt-get update
sudo apt-get install gcc g++ python python-dev mercurial bzr gdb valgrind gsl-bin libgsl-dev libgsl-dbg libgsl-dev flex bison tcpdump sqlite sqlite3 libsqlite3-dev libxml2 libxml2-dev libgtk2.0-0 libgtk2.0-dev uncrustify doxygen graphviz imagemagick python-pygraphviz python-kiwi libgoocanvas-2.0-dev python-pygccxml cmake autoconf libc6-dev libc6-dev-i386 g++-multilib texlive texlive-extra-utils texlive-latex-extra texlive-font-utils texlive-lang-portuguese dvipng git ipython libboost-signals-dev libboost-filesystem-dev openmpi-bin openmpi-common openmpi-doc libopenmpi-dev qt4-default libqt4-dev unzip p7zip-full unrar-free mercurial net-tools bridge-utils uml-utilities
sudo apt-get install python-pip python3-pip
pip install pygccxml docker
sudo pip install pygccxml pyyaml --upgrade

# Install bake

mkdir workspace
cd workspace
hg clone http://code.nsnam.org/bake

export BAKE_HOME=$(pwd)/bake
echo "export BAKE_HOME=$(pwd)/bake" >> ~/.bashrc
echo "export PATH=$PATH:$BAKE_HOME:$BAKE_HOME/build/bin" >> ~/.bashrc
echo "export PYTHONPATH=$PYTHONPATH:$BAKE_HOME:$BAKE_HOME/build/lib" >> ~/.bashrc
source ~/.bashrc

python $BAKE_HOME/bake.py check
python $BAKE_HOME/bake.py configure -e ns-3.29
python $BAKE_HOME/bake.py download
python $BAKE_HOME/bake.py build

echo "export NS3_HOME=$BAKE_HOME/../source/ns-3.29"

cd $NS3_HOME
./waf

cd ../../

# Download github repo

git clone https://gitlab.hpi.de/felix.gohla/ns3-docker.git
cd ns3-docker
