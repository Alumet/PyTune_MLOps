# Pytune AirFlow setup


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


## RUN

Initialize airflow:
```bash
docker-compose up -d
```

AirFlow web server will be available on port 
<span style="color:orange">: 8080</span>

