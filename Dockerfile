FROM python:3.11
RUN pip install poetry

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY app /app
#COPY pyproject.toml /pyproject.toml
# RUN poetry add --editable /app
# RUN poetry install
COPY  setup.py /setup.py
COPY email_model.pkl /email_model.pkl
RUN pip install -e .
ENTRYPOINT [ "python", "app/main.py" ]
