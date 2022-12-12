FROM jenkins/jenkins:alpine

USER root
RUN apk add zlib-dev jpeg-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
RUN apk add --update\
   python3 \
   python3-dev \
   build-base \
   py3-pip  \
   postgresql-dev

COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

USER jenkins
