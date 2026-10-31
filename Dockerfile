FROM python:3.16.0a1-slim-trixie

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src/crud/main.py ./code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]