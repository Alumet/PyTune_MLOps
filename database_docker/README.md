# Create mysql database

## Prefab

Pull prefab docker image populated with data (*alumet/pytune_mysql*)
```bash
docker pull alumet/pytune_mysql
docker run --name pytune_bdd -d alumet/pytune_mysql
```
Database is available on port **3306**

```json
{
  "user": "root",
  "password": "pytune",
  "database name": "main"
}
```

## Build

### Docker

Build alumet/pytune_msql using setup.sh file and Dockerfile
```bash
./setup.sh

docker run --name pytune_bdd -d alumet/pytune_msql
```

### Set UP

```bash
docker run --name pytune_bdd -d alumet/pytune_msql
docker exec -it pytune_bdd bash

mysql -uroot -p pytune # connect to MySQL

CREATE DATABASE main; #create main database
exit # exit Mysql

exit # exit container
```

### Populate

- Download .scv dataset at: https://www.dropbox.com/s/k0wmnuwn41cilmw/dataset.csv?dl=0

- Use DB_create_mysql.ipynb Notebook to populate database

