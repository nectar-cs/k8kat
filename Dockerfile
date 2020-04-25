FROM python:3.6.1

WORKDIR /app

RUN apt-get update && apt-get install -y \
                             curl \
                              apt-transport-https \
                              gnupg2 \
                              jq

RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" |  tee -a /etc/apt/sources.list.d/kubernetes.list
RUN  apt-get update && apt-get install -y kubectl

ADD Pipfile Pipfile.lock ./
RUN pip3 install pipenv
RUN pipenv install

ADD . /app

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    KAT_ENV=test \
    CONNECT_AUTH_TYPE=in \
    CONNECT_SA_NS=default \
    CONNECT_SA_NAME=nectar \
    CONNECT_CLUSTER=kind-kind \
    CONNECT_CONTEXT=kind-kind \
    CONNECT_KUBECTL=kubectl

ENTRYPOINT ["./main_image.sh"]