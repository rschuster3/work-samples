FROM python:2.7

RUN apt-get -y update

# Set up supervisord
# This will allow us to run multiple processes: celery,
# rabbitmq, and gunicorn in this case
RUN apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir /var/run/gunicorn
RUN mkdir /var/log/gunicorn

# Celery needs to be started as root
ENV C_FORCE_ROOT=1

# Place celery config and create celery user/group
COPY celeryd /etc/default/celeryd
RUN useradd -N -M --system -s /bin/bash celery
RUN groupadd celery
RUN usermod -a -G celery celery

# Create var run and log dirs and own them
RUN mkdir /var/run/celery
RUN mkdir /var/log/celery
RUN chown celery:celery /var/run/celery
RUN chown celery:celery /var/log/celery

# Install RabbitMQ
RUN apt-get -y install rabbitmq-server

# Install our own app and requirements
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8080

# Run services
CMD ["/usr/bin/supervisord"]
