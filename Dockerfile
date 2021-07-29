FROM python:slim

RUN useradd tpark

WORKDIR /home/tpark

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP main.py

RUN chown -R microblog:microblog ./
USER tpark

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
