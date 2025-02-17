FROM ubuntu:18.04

# Set noninteractive installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update

RUN apt-get install -y gir1.2-gtk-3.0

# to have add-apt-repository available
RUN apt-get install -y software-properties-common

RUN add-apt-repository ppa:gnuradio/gnuradio-releases

RUN apt-get update

RUN apt-get install -y gnuradio

# installing other packages needed for downloading and installing OOT modules
RUN apt-get install -y gnuradio-dev cmake git libboost-all-dev libcppunit-dev liblog4cpp5-dev swig liborc-dev

# of course, nothing useful can be done without vim
RUN apt-get install -y vim

ENV PYTHONPATH "${PYTHONPATH}:/usr/local/lib/python3/dist-packages"

CMD bash