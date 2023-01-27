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

docker run --name pytune_ddb -d alumet/pytune_msql
```

### Populate

- Download .scv dataset at: https://www.dropbox.com/s/k0wmnuwn41cilmw/dataset.csv?dl=0

- Use DB_create_mysql.ipynb Notebook to populate database

