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

Download dataset at:<br />
https://www.dropbox.com/s/0rpjdjnr0mgwqyw/data.rar?dl=0

Extrack .rar file your **"data"** folder

## SET UP FOLDERS

For the project to work you need to set up a few folders

- a **data** folder to store the dataset
- a **model** folder to save and store trained models

```
project
│   main.py
│   ...
└───data
│   │   dataset.csv
│   └───Fake_users
│       │   last_fm_fake_user(1001)_jazz.csv
│       │   last_fm_fake_user(1002)_classic.csv
│       │   ...
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

## RUN API

! Place yourself in folder containing main.py !
```
uvicorn main:api
```

### Test API
Open in browser:  http://127.0.0.1:8000
```bash
curl -X GET -i http://127.0.0.1:8000/
```

### Documentation
Open in browser:  http://127.0.0.1:8000/docs