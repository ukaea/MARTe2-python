FROM ubuntu:22.04

RUN apt update

# Install what is needed to build documentation and run tests
RUN apt install -y python3 graphviz python3-pip doxygen jq git nano build-essential cmake ffmpeg libsm6 libxext6 dos2unix

RUN python3 -m pip install --upgrade pip sphinx sphinx_rtd_theme breathe pytest coverage ruff pytest-qt nodeeditor pylint-gitlab pytest-cov pylint-gitlab numpy pyqt5 qtpy

WORKDIR /root

RUN mkdir /root/Projects

WORKDIR /root/Projects

RUN git clone https://github.com/aneto0/MARTe2.git -b v1.9.0

RUN git clone https://github.com/aneto0/MARTe2-components.git -b v1.8.0

RUN cd /root/Projects/MARTe2 && make -f Makefile.x86-linux core

ENV MARTe2_DIR=/root/Projects/MARTe2

RUN cd /root/Projects/MARTe2-components && make -f Makefile.x86-linux -j8 core

ENV MARTe2_Components_DIR=/root/Projects/MARTe2-components

ENV QT_QPA_PLATFORM=offscreen DISPLAY=99.0