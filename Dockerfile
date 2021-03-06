FROM python:3.7-slim

RUN apt-get --yes update && \
    mkdir -p /deploy \
    && apt-get --yes install git

WORKDIR /deploy

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install git+https://github.com/ONSdigital/pyblaise.git
RUN pip install -r requirements.txt

COPY blaise_instrument_checker blaise_instrument_checker
COPY gunicorn_config.py gunicorn_config.py
COPY wsgi.py wsgi.py
COPY settings.py settings.py

# enter application variables here
ENV FLASK_APP blaise_instrument_checker

EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/deploy/gunicorn_config.py", "wsgi:app"]
