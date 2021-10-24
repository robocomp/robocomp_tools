#!/bin/bash
# Update Ubuntu Software repository
sudo DEBIAN_FRONTEND=noninteractive apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends  \
      ca-certificates \
      cmake \
      curl \
      freeglut3-dev \
      g++ \
      gcc-multilib \
      git \
      git-annex \
      libboost-dev \
      libboost-system-dev \
      libboost-thread-dev \
      libgsl-dev \
      libopenscenegraph-dev \
      libpyside2-dev \
      libqt5opengl5-dev \
      libqt5xmlpatterns5-dev \
      libzeroc-icestorm3.7 \
      make \
      python3 \
      python3-apt \
      python3-argcomplete \
      python3-distutils \
      python3-pip \
      python3-prompt-toolkit \
      python3-pyparsing \
      python3-setuptools \
      python3-termcolor \
      python3-zeroc-ice \
      software-properties-common \
      sudo \
      zeroc-ice-all-dev \
      zeroc-icebox \
  && sudo rm -rf /var/lib/apt/lists/*

sudo pip3 install rich typer pyside2

# Some incompatibility from pyside2 (5.15) and default qt installation (5.14)
#echo "Installation fix for $(cat /etc/issue | grep '20.04')"
#if cat /etc/issue | grep '20.04' ; then
#  sudo add-apt-repository ppa:beineri/opt-qt-5.15.2-focal
#  sudo apt-get update
#  sudo apt-get install qt515base -y
#  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/qt515/lib/
#  sudo pip3 install Pyside2
#else
#  sudo DEBIAN_FRONTEND=noninteractive apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends  \
#        python3-pyside2.qtcore \
#        python3-pyside2.qtwidgets \
#    && sudo rm -rf /var/lib/apt/lists/*
#fi
