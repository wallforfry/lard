FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code

RUN echo "deb http://deb.debian.org/debian sid main" >> /etc/apt/sources.list.d/sid.list && apt update && apt install glibc-source libc6 libstdc++6 -y 

WORKDIR /code
ADD ./tensorflow-1.13.1-cp36-cp36m-linux_x86_64.whl /code/
RUN pip install tensorflow-1.13.1-cp36-cp36m-linux_x86_64.whl

ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
