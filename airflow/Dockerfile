FROM apache/airflow:latest-python3.10

USER root

COPY requirements.txt . 

RUN apt update
RUN sudo apt install libgomp1

USER airflow

RUN pip install -r requirements.txt
