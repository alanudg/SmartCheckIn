FROM ubuntu:xenial
MAINTAINER Alan Sanchez <alan.sanchez@alumnos.udg.mx>

ENV DEBIAN_FRONTEND noninteractive
ENV MYSQLTMPROOT temprootpass
ENV MARIADB_MAJOR 10.1
ENV MARIADB_VERSION 10.1.19+maria-1~xenial

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN groupadd -r mysql && useradd -r -g mysql mysql

#Add keys [mongodb and mariadb]
RUN apt-get update && apt-get install -y software-properties-common \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927 \
    && echo 'deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse' | tee /etc/apt/sources.list.d/mongodb-org-3.2.list
    #&& apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8 \
    #&& add-apt-repository "deb [arch=amd64,i386,ppc64el] http://ftp.utexas.edu/mariadb/repo/$MARIADB_MAJOR/ubuntu xenial main" \
    #&& apt-get update

#Install dependencies
RUN apt-get install -y \
    python-pip python-dev uwsgi-plugin-python python-mysqldb \
    supervisor nodejs-legacy git npm \
    && npm install -g bower

#Install mongodb
RUN apt-get install -y mongodb-org \
    && mkdir -p /data/db

#Install nginx
RUN apt-get install -y nginx

COPY mariadb_secure_install.sh /tmp/mariadb_secure_install.sh
# Install mariadb
RUN { \
    	echo mariadb-server-${MARIADB_MAJOR} mysql-server/root_password password "${MYSQLTMPROOT}"; \
    	echo mariadb-server-${MARIADB_MAJOR} mysql-server/root_password_again password "${MYSQLTMPROOT}"; \
    } | debconf-set-selections \
    && apt-get install -y mariadb-server=${MARIADB_VERSION} expect && chown mysql /var/log/mysql \
    # comment out any "user" entires in the MySQL config ("docker-entrypoint.sh" or "--user" will handle user switching)
    #&& sed -ri 's/^user\s/#&/' /etc/mysql/my.cnf /etc/mysql/conf.d/* \
    # purge and re-create /var/lib/mysql with appropriate ownership
    && rm -rf /var/lib/mysql && mkdir -p /var/lib/mysql /var/run/mysqld \
    && chown -R mysql:mysql /var/lib/mysql /var/run/mysqld \
    # ensure that /var/run/mysqld (used for socket and lock files) is writable regardless of the UID our mysqld instance ends up having at runtime
    && chmod 777 /var/run/mysqld \
    && mysql_install_db \
    && apt-get install -y libmysqlclient-dev
    #&& echo -e "\n\n${MYSQLTMPROOT}\n${MYSQLTMPROOT}\n\n\nn\n\n " | mysql_secure_installation 2>/dev/null
    #&& mysql_secure_installation

CMD ["/tmp/mariadb_secure_install"]

RUN apt-get -y purge expect

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
    && easy_install MySQL-python \
    && cd /var/www/app \
    && npm install \
    && bower install --allow-root

CMD ["/usr/bin/supervisord"]
