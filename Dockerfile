FROM python:3.9.5

# Install yarn
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt update && apt install -y yarn

# Copy requirements.txt and install python dependencies
RUN mkdir usr/app/
RUN mkdir usr/app/src/
COPY requirements.txt usr/app/
RUN pip install -r /usr/app/requirements.txt

## Copy custom components and run the compilation script
#COPY custom_components/ usr/app/custom_components/
#COPY build_custom_components.sh usr/app/
#WORKDIR usr/app/
#RUN ./build_custom_components.sh

# Copy the app and the dataset
COPY src src
COPY dataset dataset

# Set environment to PROD and start the app
ENV ENV=PROD
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --preload --pythonpath src/ app:server
