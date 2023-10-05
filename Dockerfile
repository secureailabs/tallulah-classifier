FROM python:3.8

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app

WORKDIR /app

ENTRYPOINT [ "python3", "main.py" ]
