# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

ENV LISTEN_PORT=5000
EXPOSE 5000

COPY venv/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV PYTHONPATH ./venv

COPY . .

# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# CMD [ "flask", "--app", "venv/app.py", "--debug", "run" ]

CMD [ "flask", "run" ]
