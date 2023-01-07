from fastapi.testclient import TestClient
import pytest
from api import app
from utils.data import DataBase
from model.model import als_model
import numpy as np
import pandas as pd

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'Api status': 'running'}


def test_recommendation(mocker):
    user = {'username': 'admin',
            'hashed_password': '$2b$12$026/Xg0uN/Z5lJHQpGDQzu8VEsInOqRFZ6qwFe5mRI.TzRl5In2OK',
            'id': 0}

    mocker.patch.object(DataBase.instance(), 'get_user_info', return_value=user)

    df = pd.DataFrame({"track_id": [1, 2],
                       "track_name": ['track_1', 'track_2'],
                       "artist_id": [0, 0],
                       "artist_name": ['artist_0', 'artist_0']
                       })

    mocker.patch.object(DataBase.instance(), 'get_track_info', return_value=df)

    mocker.patch.object(als_model, 'recommend', return_value=(np.array([1, 2]), np.array([0, 0])))

    data = {"N_track": 10,
            "filter_already_liked": False
            }

    response = client.post('/recommendation',
                           auth=("admin", "admin"),
                           json=data)

    assert response.status_code == 200
    assert type(response.json()) == dict
