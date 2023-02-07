# Pytune

Pytune is an MLOps project that take place in a 
Datascientest training. The goal is to put into production 
a music recommender model based on the Implicit python 
library trained on the last.fm 1k dataset

This project put into action multiple technologies:
- FastApi (pytune api)
- MySQL (pytune database)
- Docker and docker-compose (virtualization)
- AirFlow (automation and model training)
- GitHub actions (CI/CD, unit test, docker build)

# 1 - DOCUMENTATION

Both reports documenting "data science" and "MLOps" aspect of the projetc
are available int the documentation root directory.

- Rapport fil rouge - Datascientest - PyTune.pdf
- Rapport MLOps - Datascientest - PytTune.pdf

```
project
│
└───documentation
│   │ Rapport fil rouge - Datascientest - PyTune.pdf
│   │ Rapport MLOps - Datascientest - PytTune.pdf
```

# 2 - THE PROJECT

The project is build with modularity in mind so your not obliged to 
run all component. Sub-applications orchestrate around a core 
application. In order to make things simple all docker-compose uses 
the same predefined network (pytune). 

- **CORE APP**
  - docker: pytune_api + pytune_bdd 
  - purpose: recommendation api and data base 

- **AIRFLOW**
  - docker: airflow
  - purpose: automation and monitoring
  
- **WEB APP**
  - docker: pytune_webapp
  - purpose: front user interface

# 3 - INSTALLATION

Set up and run pytune API and DataBase. Two options are available:
- using docker-compose
- using python

## 3.1 - WITH DOCKER-COMPOSE

You can either build your own docker images using provided 
Dockerfiles or pull prefab from dockerhub

>### CORE APP
>
> - alumet/pytune_api:latest
> - alumet/pytune_mysql:latest
>
>#### Build (optional)
>
>- pytune_api
>```bash
>docker image build . -t alumet/pytune_api:latest
>```
>
>- pytune_bdd
>
>  Follow instruction in database_docker/README.md
>```
> project
> └───database_docker
> │   │ README.md
> ```
>#### RUN
>```bash
># run core app (api + bdd)
>docker-compose up -d
>```

>#### WEB APP
> ```
> project
> │
> └───webapp
> │   │
> ```
> - alumet/pytune_webapp:latest
>#### Build (optional)
>Follow instruction in webapp/README.md
> ```
> project
> └───webapp
> │   │ README.md
> ```
>#### RUN
>```bash
># run webapp
>cd webapp
>docker-compose up -d 
>```

>#### AIRFLOW
>Follow instruction in airflow/README.md
> ```
> project
> └───airflow
> │   │ README.md
> ```

## 3.2 - WITH PYTHON (3.8 or higher)

Update
```bash
atp update

apt install python3-dev default-libmysqlclient-dev build-essential python3-pip
```

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

```
project
└───database_docker
│   │ README.md
```

### SET UP .env FILE

Create .env file from template
```bash
cp .env_template .env
```
File all Environment Variables with:
- DATA_BASE: url to database (mysql)
- MODEL_FOLDER: model folders (default production)
- PRODUCTION_MODEL: production model (default als_model.mdl)

## RUN API

! Place yourself in folder containing api.py !
```
uvicorn api:app
```

# 4 - Test API
For both methods python or docker, open in browser:  http://127.0.0.1:8000

Or test using curl
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

## 5 - FIRST MODEL

This cam be long (up to 15 min) and require at least 
6Go of RAM

>Once the model trained it should have been saved in then model folder
>```
>project
>└───production
>│   │ model_asl.mdl
>```

### 5.2 - using pretrained model
Download model at https://www.dropbox.com/s/z8p5knhkn88884a/model_als.mdl?dl=0

Place file model_als.mdl in **production** folder


### 5.2 - using python installation
Step 3.2 required
```bash
# from project folder
python3 train.py
```

### 5.3 - using API
```bash
curl -X GET \
-i http://127.0.0.1:8000/admin/model/train \
-u "admin:admin"
```

### 5.4 - using Airflow
See airflow/Readme.md to set up
```
project
└───airflow
│   │ README.md
```

### 6 - RELOAD NEW MODEL
Load new model in API. Restart API server or use reload end point
```bash
curl -X GET \
-i http://127.0.0.1:8000/admin/model/reload \
-u "admin:admin"
```


### 7 - API USE EXAMPLE

Search track title containing "smells"
```bash
curl -X POST \
-i http://127.0.0.1:8000/search?search=smells \
-u "admin:admin"
```

Personalised Recommendation (change with user)
```bash
curl -X POST \
-i http://127.0.0.1:8000/recommendation \
-u "admin:admin" \
-d '{"N_track": 10,"filter_already_liked": false}'  \
-H 'Content-Type: application/json'
```

Add new user
```bash
curl -X POST \
-i http://127.0.0.1:8000/admin/user \
-u "admin:admin" \
-d '{"user_name": "aa", "pass_word": "aa", "is_admin": false}' \
-H 'Content-Type: application/json'
```


