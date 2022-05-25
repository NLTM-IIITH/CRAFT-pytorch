FROM python:3.6.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache -r requirements.txt

RUN apt update && apt install -y libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx

COPY . .