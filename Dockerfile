FROM python:3.11

COPY tallulah_classifier /tallulah_classifier

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY app /app

ENTRYPOINT [ "python3", "app/main.py" ]
