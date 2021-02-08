#!/bin/bash
cat /etc/issue

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
    libqt5xmlpatterns5-dev \
    libqt5opengl5-dev \
    make \
    python3 \
    python3-pip \
    python3-distutils \
    python3-prompt-toolkit \
    python3-pyparsing \
    python3-setuptools \
    python3-termcolor \
    sudo \
    zeroc-ice-all-dev \
    && rm -rf /var/lib/apt/lists/*

sudo pip3 pyside2
