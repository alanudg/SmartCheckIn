FROM ubuntu:xenial
MAINTAINER Alan Sanchez <alan.sanchez@alumnos.udg.mx>

ENV DEBIAN_FRONTEND noninteractive

#Add keys [mongodb and mariadb]
RUN apt-get update && apt-get install -y software-properties-common \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927 \
    && echo 'deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse' | tee /etc/apt/sources.list.d/mongodb-org-3.2.list

#Install dependencies
RUN apt-get install -y \
    python-pip python-dev uwsgi-plugin-python python-psycopg2\
    supervisor nodejs-legacy git npm \
    && npm install -g bower

#Install mongodb
RUN apt-get install -y mongodb-org \
    && mkdir -p /data/db

#Install nginx
RUN apt-get install -y nginx

# Install postgresql
RUN apt-get install -y postgresql postgresql-contrig
    && apt-get install -y libmysqlclient-dev libgeos-dev


COPY flask.conf /etc/nginx/sites-available/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY . /var/www/app



RUN mkdir -p /var/log/nginx/app /var/log/uwsgi/app /var/log/supervisor \
    && rm /etc/nginx/sites-enabled/default \
    && ln -s /etc/nginx/sites-available/flask.conf /etc/nginx/sites-enabled/flask.conf \
    && echo "daemon off;" >> /etc/nginx/nginx.conf \
    && chown -R www-data:www-data /var/www/app
    #&& chown -R www-data:www-data /var/log

#Install flask, npm and bower dependencies
RUN pip install --upgrade pip \
    && pip install -r /var/www/app/requirements.txt \
    #&& easy_install  \
    && cd /var/www/app \
    && npm install \
    && bower install --allow-root

CMD ["/usr/bin/supervisord"]
