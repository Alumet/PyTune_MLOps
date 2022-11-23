# Pytune

pytune is an MLOps project that take place in a Datascientest training

## INSTALLATION

Install requirements:
```bash
pip install -r requirements.txt
```

Install uvicorn server with:
```bash
sudo apt install uvicorn
```

## GET DATASET

Download database at:<br />
https://www.dropbox.com/s/amcndwbpfd7ev6i/pytune.db?dl=0

## SET UP FOLDERS

For the project to work you need a few folders

- a **data** folder to store the dataset
- a **model** folder to save and store trained models

```
project
│   api.py
│   ...
│
└───data
│   │   pytune.db
│   │ ...
│
└───model
│   │ ...
```

## SET UP .env FILE

Create .env file from template
```bash
cp .env_template .env
```
File all Environment Variables with path to your data and model folders

## TRAIN MODEL

Train first model or retrain
```bash
python3 train.py
```
Once the model trained it should have been saved in then model folder
```
project
│
└───model
│   │ model_asl.mdl
```

## RUN API

! Place yourself in folder containing api.py !
```
uvicorn api:app
```

### Test API
Open in browser:  http://127.0.0.1:8000
```bash
curl -X GET -i http://127.0.0.1:8000/
```

### Documentation
Open in browser:  http://127.0.0.1:8000/docs

### API DEFAULT USERS

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

