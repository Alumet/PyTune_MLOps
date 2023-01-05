FROM debian:latest

copy . /app
WORKDIR /app/

RUN apt update
RUN echo "y" | apt install python3-dev default-libmysqlclient-dev build-essential python3-pip
RUN pip install -r requirements.txt

ENV MODEL_FOLDER='production/'
ENV PRODUCTION_MODEL='production/model_als.mdl'
ENV DATA_BASE='mysql://root:pytune@localhost/main'

EXPOSE 8000

CMD uvicorn api:app --reload --host 0.0.0.0
