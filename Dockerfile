FROM python:slim

COPY app /app

RUN adduser -u 5000 app --disabled-password
RUN chown -R app:app /app

USER app

WORKDIR /code

CMD python /app/run.py
