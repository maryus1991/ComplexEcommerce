FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECCODE=1
ENV PYTHONNONBUFFERED=1

WORKDIR /app


ENV CURLOPT_SSL_VERIFYHOST=0
ENV CURLOPT_SSL_VERIFYPEER=0
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY req.txt req.txt
COPY /admin_panel/ /app/
COPY /blog/ /app/
COPY /config/ /app/
COPY /dashboard/ /app/
COPY /orders/ /app/
COPY /product/ /app/
COPY /sitesetting/ /app/
COPY /stores/ /app/
COPY /templates/ /app/
COPY /user/ /app/
COPY 1111.jpg /app/
COPY manage.py /app/
COPY ZARINPAL_ERRORS.py /app/
COPY .envs /app/

RUN pip install -r req.txt


