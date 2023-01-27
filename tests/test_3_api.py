from fastapi.testclient import TestClient
import pytest
from api import app
from utils.data import DataBase
from model.model import als_model
import numpy as np
import pandas as pd
from utils import erros

client = TestClient(app)


@pytest.fixture
def admin_log(mocker):
    user = {'username': 'admin',
            'admin': True,
            'hashed_password': '$2b$12$026/Xg0uN/Z5lJHQpGDQzu8VEsInOqRFZ6qwFe5mRI.TzRl5In2OK',
            'id': 0}

    mocker.patch.object(DataBase.instance(), 'get_user_info', return_value=user)


@pytest.fixture
def user_log(mocker):
    user = {'username': 'admin',
            'admin': False,
            'hashed_password': '$2b$12$026/Xg0uN/Z5lJHQpGDQzu8VEsInOqRFZ6qwFe5mRI.TzRl5In2OK',
            'id': 0}

    mocker.patch.object(DataBase.instance(), 'get_user_info', return_value=user)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'Api status': 'running'}


def test_auth(mocker):
    mocker.patch.object(DataBase.instance(), 'get_user_info', side_effect=erros.UserDoesNotExist)

    response = client.post('/login',
                           auth=("admin", "admin")
                           )

    assert response.status_code == 405


@pytest.mark.usefixtures("admin_log")
def test_recommendation(mocker):
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


@pytest.mark.usefixtures("admin_log")
def test_event(mocker):
    mocker.patch.object(DataBase.instance(), 'add_event', return_value=None)

    data = {"track_id": 10}

    response = client.post('/event',
                           auth=("admin", "admin"),
                           json=data)

    assert response.status_code == 200
    assert response.json() == {'status': 'success'}


@pytest.mark.usefixtures("admin_log")
def test_reload_model_admin(mocker):
    mocker.patch.object(als_model, 'load', return_value=None)

    response = client.get('admin/model/reload',
                          auth=("admin", "admin"))

    assert response.status_code == 200
    assert response.json() == {'status': 'model reloaded'}


@pytest.mark.usefixtures("user_log")
def test_reload_model_user(mocker):
    mocker.patch.object(als_model, 'load', return_value=None)

    response = client.get('admin/model/reload',
                          auth=("admin", "admin"))

    assert response.status_code == 403


@pytest.mark.usefixtures("admin_log")
def test_train_model_admin(mocker):

    mocker.patch('api.train_model', return_value=None)

    response = client.get('admin/model/train',
                          auth=("admin", "admin"))

    assert response.status_code == 200
    assert response.json() == {'status': 'model trained'}


@pytest.mark.usefixtures("user_log")
def test_train_model_user(mocker):

    mocker.patch('api.train_model', return_value=None)

    response = client.get('admin/model/train',
                          auth=("admin", "admin"))

    assert response.status_code == 403


@pytest.mark.usefixtures("admin_log")
def test_add_user_admin(mocker):
    mocker.patch.object(DataBase.instance(), 'add_user', return_value=None)

    data = {"user_name": 'test',
            'pass_word': 'test',
            'is_admin': False}

    response = client.post('admin/user',
                           auth=("admin", "admin"),
                           json=data)

    assert response.status_code == 200
    assert response.json() == {'status': 'user added'}


@pytest.mark.usefixtures("user_log")
def test_add_user_user(mocker):
    mocker.patch.object(DataBase.instance(), 'add_user', return_value=None)

    data = {"user_name": 'test',
            'pass_word': 'test',
            'is_admin': False}

    response = client.post('admin/user',
                           auth=("admin", "admin"),
                           json=data)

    assert response.status_code == 403


@pytest.mark.usefixtures("admin_log")
def test_user_recommendation_admin(mocker):
    df = pd.DataFrame({"track_id": [1, 2],
                       "track_name": ['track_1', 'track_2'],
                       "artist_id": [0, 0],
                       "artist_name": ['artist_0', 'artist_0']
                       })

    mocker.patch.object(DataBase.instance(), 'get_track_info', return_value=df)

    mocker.patch.object(als_model, 'recommend', return_value=(np.array([1, 2]), np.array([0, 0])))

    data = {"N_track": 10,
            "filter_already_liked": False,
            'user_id': 1
            }

    response = client.post('admin/recommendation',
                           auth=("admin", "admin"),
                           json=data)

    assert response.status_code == 200
    assert type(response.json()) == dict


@pytest.mark.usefixtures("user_log")
def test_user_recommendation_admin(mocker):
    df = pd.DataFrame({"track_id": [1, 2],
                       "track_name": ['track_1', 'track_2'],
                       "artist_id": [0, 0],
                       "artist_name": ['artist_0', 'artist_0']
                       })

    mocker.patch.object(DataBase.instance(), 'get_track_info', return_value=df)

    mocker.patch.object(als_model, 'recommend', return_value=(np.array([1, 2]), np.array([0, 0])))

    data = {"N_track": 10,
            "filter_already_liked": False,
            'user_id': 1
            }

    response = client.post('admin/recommendation',
                           auth=("admin", "admin"),
                           json=data)

    assert response.status_code == 403