FROM python:3.11.6

## make a local directory
RUN mkdir /app
RUN mkdir -p /TRex/efs
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 tesseract-ocr -y

RUN pip install  -r requirements.txt

EXPOSE 5000

CMD [ "python3", "main.py"]