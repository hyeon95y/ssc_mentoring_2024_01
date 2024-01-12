# Install Python 3.8.10
FROM python:3.8.10
# Maintainer info.
MAINTAINER Hyeonwoo Daniel Yoo <hyeon95y@gmail.com> 


# Install direnv, make, vim, git, pip
RUN apt-get update && \ 
    apt-get install -y direnv make vim git && \ 
    echo 'eval "$(direnv hook bash)"' >> ~/.bashrc && \
    pip install --upgrade pip

# working directory
WORKDIR /root


# Clone repository and install python packages using Makefile
RUN git clone https://github.com/hyeon95y/ssc_mentoring_2024_01.git && \
    cd ssc_mentoring_2024_01 && \
    make setup -i

# Inject credentials into the image
COPY src/_secrets.py ssc_mentoring_2024_01/src
RUN mkdir .aws
COPY config .aws
COPY credentials .aws 