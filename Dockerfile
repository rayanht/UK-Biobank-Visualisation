FROM python:3.8

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt update && apt install -y yarn
RUN pip install pipenv
RUN mkdir usr/app/
RUN mkdir usr/app/src/
COPY src/ usr/app/src/
COPY Pipfile usr/app/
COPY build_custom_components.sh usr/app/
ADD Pipfile.lock usr/app/
WORKDIR usr/app/
RUN ls src/
RUN pipenv install --system --deploy --ignore-pipfile
RUN ./build_custom_components.sh

CMD ["pipenv", "run", "gunicorn", "-b", "0.0.0.0:$PORT" , "--pythonpath", "src/", "app:server"]