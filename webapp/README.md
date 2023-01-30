# WebApp setup

## Python

install requirements
```bash
pip install -r ../requirements.txt
```

run server
```bash
streamlit run app.py --server.port 9000
```

webapp should be available on http://localhost:9000


## Docker
you can build docker image or use prefab alumet/pytune_webapp:latest

### build
```bash
./seup.sh
```

### Run docker-compose
All docker-compose are set up to run on the same network(pytune) to allow communication between services 
```bash
docker-compose up -d
```

webapp should be available on http://localhost:9000