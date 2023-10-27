FROM python:3.11

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY app /app
COPY email_model.pkl /email_model.pkl

ENTRYPOINT [ "python3", "-m", "app.main" ]
