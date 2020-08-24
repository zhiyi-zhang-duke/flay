FROM ubuntu:latest
ADD app/ /app
WORKDIR /app
RUN apt-get update -y && \
	apt-get install -y python3-pip python-dev build-essential
RUN pip3 install -r requirements.txt
RUN pip3 install flask
RUN pip3 install progress
ENTRYPOINT ["python3"]
CMD ["app.py"]