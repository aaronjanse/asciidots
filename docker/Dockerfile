FROM python:3

WORKDIR /code

RUN pip3 install --no-cache-dir click
COPY . /code

ENTRYPOINT ["python", "__main__.py"]
