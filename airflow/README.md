# AirFlow setup

## INSTALLATION

Create folders:
```bash
mkdir ./dags ./logs ./plugins
```

Add requirement file:
```bash
cp ../requirements.txt .
```

Create .env file:
```bash
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
```

Initialize airflow:
```bash
docker-compose up airflow-init
```
Return should be
<span style="color:orange">: **start_airflow-init_1 exited with code 0**</span>

## ADD DAGS

```bash
git clone https://github.com/Alumet/pytune.git dags
```

## DOWNLOAD CSV DATASET

- Download dataset at: https://www.dropbox.com/s/k0wmnuwn41cilmw/dataset.csv?dl=0
- Copy <span style="color:orange">dataset.csv</span> file in the <span style="color:orange">data</span> folder
## RUN

Run airflow:
All docker-compose are set up to run on the same network(pytune) to allow communication between services 
```bash
docker-compose up -d
```

AirFlow web server will be available on port 
<span style="color:orange">: 8080</span>

- user: airflow
- password: airflow

