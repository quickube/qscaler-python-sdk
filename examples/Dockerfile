FROM python:3.11-alpine

WORKDIR /app

RUN pip install poetry

COPY . .

RUN poetry env use python
RUN poetry install

COPY ./examples/worker.py ./worker.py

CMD ["poetry", "run", "python3", "/app/worker.py"]