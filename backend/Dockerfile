FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3-pip
RUN apt-get install -y python2.7-dev build-essential
COPY . /app
WORKDIR /app 
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]