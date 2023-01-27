# Pytune

Pytune is an MLOps project that take place in a Datascientest training.
The project is to put into production a music recommender model based on
the Implicit python library trained on the last.fm 1k dataset (cf documentation/Rapport fil rouge - Datascientest - PyTune.pdf)

This project put into action multiple technologies:
- FastApi (pytune api)
- MySQL (pytune database)
- Docker and docker-compose (virtualization)
- AirFlow (automation and model training)
- GitHub actions (CI/CD, unit test, docker build)

# 1 - INSTALLATION

Set up and run pytune API and DataBase. Two options available:
- using docker-compose
- using python

## 1.1 - WITH DOCKER-COMPOSE
This methode use two docker images:
- alumet/pytune_api:latest
- alumet/pytune_mysql:latest

You can either build your own docker images using provided Dockerfiles or pull prefab from dockerhub

```bash
docker-compose up -d
```

## 1.2 - WITH PYTHON (3.8 or higher)

Install requirements:
```bash
pip install -r requirements.txt
```

Install uvicorn server with:
```bash
sudo apt install uvicorn
```

### GET DATABASE

Follow instruction from database_docker/Readme.md

### SET UP .env FILE

Create .env file from template
```bash
cp .env_template .env
```
File all Environment Variables with:
- url to database (mysql)
- model folders (default production)
- production model (default als_model.mdl)

## RUN API

! Place yourself in folder containing api.py !
```
uvicorn api:app
```

# 2 - Test API
For both methods python or docker, open in browser:  http://127.0.0.1:8000
```bash
curl -X GET -i http://127.0.0.1:8000/
```

## Documentation
Open in browser:  http://127.0.0.1:8000/docs

## Api default users

**admin user**
```json
{
  "id": 0,
  "username": "admin",
  "password": "admin"
}
```

**test fakes users**
```json
{
  "jazz":{
    "id": 960,
    "username": "user_jazz",
    "password": "jazz"
  },
  "classic":{
    "id": 961,
    "username": "user_classic",
    "password": "classic"
  },
  "pop":{
    "id": 962,
    "username": "user_pop",
    "password": "pop"
  },
  "rock":{
    "id": 963,
    "username": "user_rock",
    "password": "rock"
  },
  "rap":{
    "id": 964,
    "username": "user_rap",
    "password": "rap"
  }
}
```

## 3 - TRAIN FIRST MODEL

### 3.1 - using python installation
Step 2.1 required
```bash
python3 train.py
```

### 3.2 - using api
```bash
curl -X GET -i http://127.0.0.1:8000/admin/model/train -u "admin:admin"
```
This cam be long (up to 10 min)

### 3.3 - using Airflow
See airflow/Readme.md to set up


Once the model trained it should have been saved in then model folder
```
project
│
└───production
│   │ model_asl.mdl
```


### 4 - RELOAD NEW MODEL
Load new mode in API
```bash
curl -X GET -i http://127.0.0.1:8000/admin/model/reload -u "admin:admin"
```





