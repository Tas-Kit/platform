FROM python:3
ADD . /platform/
WORKDIR /platform
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN apt-get update
RUN apt-get install -y gettext nano
CMD ./manage.py runserver -p 8000 -h 0.0.0.0
