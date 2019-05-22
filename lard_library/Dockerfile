FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /lard_library

RUN echo "deb http://deb.debian.org/debian sid main" >> /etc/apt/sources.list.d/sid.list && apt update && apt install glibc-source libc6 libstdc++6 cmake -y

WORKDIR /lard_library
ADD ./tensorflow-1.13.1-cp36-cp36m-linux_x86_64.whl /lard_library/
RUN pip install tensorflow-1.13.1-cp36-cp36m-linux_x86_64.whl

WORKDIR /tmp
RUN git clone https://github.com/davisking/dlib.git && cd dlib && mkdir build; cd build; cmake ..; cmake --build . && cd .. && python3 setup.py install && rm -rf /tmp/dlib

WORKDIR /lard_library
ADD requirements.txt /lard_library/
RUN pip install -r requirements.txt

EXPOSE 12300
WORKDIR /
ADD ./run.sh /
ENV FLASK_APP="./worker.py"
ADD ./worker.py /

ADD . /lard_library/
CMD ["bash", "run.sh"]