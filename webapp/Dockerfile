FROM debian:latest

copy . /app
WORKDIR /app/

RUN apt update
RUN echo "y" | apt install python3-dev default-libmysqlclient-dev build-essential python3-pip
RUN pip install -r requirements.txt

ENV API_URL='http://127.0.0.1:8000'

EXPOSE 9000

CMD streamlit run app.py --server.port 9000
