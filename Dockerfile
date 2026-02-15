###########
# BUILDER #
###########

# pull official base image
FROM python:3.14-trixie AS builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip poetry poetry-plugin-export

COPY pyproject.toml .
# COPY poetry.lock .

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels gunicorn

#########
# FINAL #
#########

FROM python:3.14-slim-trixie

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system --group app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

WORKDIR /home/app

# install dependencies
RUN sed -i "s/Components: main/Components: main non-free/" /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y --no-install-recommends default-libmysqlclient-dev nginx poppler-utils unrar-free p7zip-full unrar pdftk

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*
RUN pip install python-dotenv


# copy project
COPY . /home/app

# RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/sites-enabled/default
# COPY nginx/nginx.conf /etc/nginx/conf.d

WORKDIR /home/app

# chown all the files to the app user
RUN chown -R app:app /home/app

# change to the app user
# USER app

RUN chmod +x launcher.sh
CMD /home/app/launcher.sh

EXPOSE 80