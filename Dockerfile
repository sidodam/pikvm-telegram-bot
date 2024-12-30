FROM python:3.9-slim
WORKDIR /pikvm
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./app ./app
CMD [ "python",  "-u", "./app/main.py"]