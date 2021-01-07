FROM python:3.8

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt update && apt install -y yarn
RUN pip install pipenv

RUN mkdir usr/app/
RUN mkdir usr/app/src/
COPY src/ usr/app/src/
COPY Pipfile* usr/app/
RUN cd /usr/app/ && pipenv lock --requirements > requirements.txt
RUN pip install -r /usr/app/requirements.txt

COPY build_custom_components.sh usr/app/
WORKDIR usr/app/
RUN ./build_custom_components.sh

ENV ENV=PROD
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 0 --pythonpath src/ app:server
