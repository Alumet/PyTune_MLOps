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

Download .scv dataset at

use DB_create_mysql.ipynb Notebook to populate database
