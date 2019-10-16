FROM python:3-slim

MAINTAINER n1trux
RUN apt-get update &&\
    apt-get -y upgrade &&\
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
     nano rsync openssh-server acl

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# create user for applications
RUN useradd -Md /app/user/ -s /app/user/userapplication.py tilde

# make tilde's password empty
RUN passwd -d tilde
RUN usermod -U tilde

# add admin user
RUN useradd -Md /app/admin -s /app/admin/administrate.py admin
# privilege separation directory
RUN mkdir -p /var/run/sshd
# expose SSH port
EXPOSE 22
ENV TILDE_CONF="/app/data/applicationsconfig.ini"

# private/{scripts, administrate.py}, public/{scripts, userapplications.py}, config/userapplicatonsconfig.ini
#configs, logs, db
COPY config/applicationsconfig.ini /app/data/applicationsconfig.ini

# admin scripts
COPY private/ /app/admin/

# user accessible scripts
# Make TILDE_ENV 
COPY public/ /app/user/
#SSH config into /etc :)
COPY config/etc /etc

RUN touch /app/data/applications.sqlite
RUN touch /app/data/applications.log
#  Doesnt work, @TODO why
#RUN setfacl -R -m u:tilde:rwx /app/data/
RUN chown -R tilde  /app/data
RUN mkdir /app/user/.ssh
CMD ["sh", "-c", " echo TILDE_CONF=$TILDE_CONF > /app/user/.ssh/environment && /usr/sbin/sshd -D"]
