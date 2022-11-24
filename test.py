import datetime
import os

import data
import model
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import erros
import pytest
import pickle

import sqlite3, sqlalchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData, create_engine, text, inspect, Boolean, \
    Date, Float

""" model.py test """


def test_model():
    m = model.als_model(factors=10,
                        iterations=20,
                        alpha=30)
    assert m.factors == 10
    assert m.iterations == 20
    assert m.alpha == 30


def test_model_train():
    m = model.als_model(factors=10,
                        iterations=1,
                        alpha=1)

    train = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))
    test = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))

    m.train(train, test)

    assert m.model_music is not None


def test_model_score_untrained():
    m = model.als_model()
    with pytest.raises(erros.ModelNotTrained):
        m.score()


def test_model_score_trained():
    m = model.als_model(factors=10,
                        iterations=1,
                        alpha=1)

    train = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))
    test = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))

    m.train(train, test)

    score = m.score()
    assert type(score) == dict


def test_model_recommend_trained():
    m = model.als_model(factors=10,
                        iterations=1,
                        alpha=1)

    train = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))
    test = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))

    m.train(train, test)

    reco = m.recommend(user_id=1, nb_tracks=2)

    assert type(reco) == tuple
    assert len(reco) == 2
    assert type(reco[0]) == np.ndarray
    assert type(reco[1]) == np.ndarray


def test_model_recommend_untrained():
    m = model.als_model()
    with pytest.raises(erros.ModelNotTrained):
        reco = m.recommend(user_id=1, nb_tracks=2)


def test_model_save_untrained(tmpdir):
    m = model.als_model()
    path = f'{tmpdir}\\'
    with pytest.raises(erros.ModelNotTrained):
        m.save(path)


def test_model_save_trained(tmpdir):
    m = model.als_model(factors=10,
                        iterations=1,
                        alpha=1)

    train = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))
    test = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))

    m.train(train, test)

    path = f'{tmpdir}\\'
    m.save(path=path)
    assert 'model_als.mdl' in os.listdir(path)


def test_model_load(tmpdir):
    path = f'{tmpdir}\\'
    with open(path + 'model_als.mdl', 'wb') as file:
        pickle.dump(('model',
                     'mat_train',
                     'mat_test'), file)

    m = model.als_model()
    m.load(path + 'model_als.mdl')


""" test DataBase"""


def test_database():
    os.environ['DATA_BASE'] = ":memory:"
    db = data.DataBase.instance()
    assert db


@pytest.fixture
def database():
    os.environ['DATA_BASE'] = ":memory:"
    db = data.DataBase.instance()
    yield db


@pytest.fixture
def setup_db(database):
    meta = MetaData()

    user = Table(
        'user', meta,
        Column('id', Integer, primary_key=True),
        Column('name', String, unique=True),
        Column('admin', Boolean),
        Column('hashed_password', String),
        extend_existing=True,
    )

    artist = Table(
        'artist', meta,
        Column('id', Integer, primary_key=True),
        Column('name', String, unique=True),
        extend_existing=True,
    )

    track = Table(
        'track', meta,
        Column('id', Integer, primary_key=True),
        Column('title', String),
        Column('artist_id', Integer, ForeignKey('artist.id')),
        Column('artist_name', String),
        extend_existing=True,
    )

    user_item = Table(
        'user_item', meta,
        Column('user_id', Integer, ForeignKey('user.id')),
        Column('track_id', Integer, ForeignKey('track.id')),
        Column('time_stamp', Date),
        extend_existing=True,
    )

    prediction = Table(
        'prediction', meta,
        Column('user_id', Integer, ForeignKey('user.id')),
        Column('track_ids', String),
        Column('time_stamp', Date),
        extend_existing=True,
    )

    training = Table(
        'training', meta,
        Column('time_stamp', Date),
        Column('sample', Integer),
        Column('precision', Float),
        Column('map', Float),
        Column('ndcg', Float),
        Column('auc', Float),
        extend_existing=True,
    )

    meta.create_all(database.engine)

    with database.engine.connect() as connection:
        with connection.begin() as transaction:
            values = [(0, 'admin', True, 'ezrar')]
            connection.execute(f"INSERT OR REPLACE INTO user VALUES (?,?,?,?)", values)

            values = [(0, 'artist_0')]
            connection.execute(f"INSERT OR REPLACE INTO artist VALUES (?,?)", values)

            values = [(0, 'song_0', 0, 'artist_0'), (1, 'song_1', 0, 'artist_0')]
            connection.execute(f"INSERT OR REPLACE INTO track VALUES (?,?,?,?)", values)

            values = [(0, 0, '2022-05-01'), (0, 1, '2022-05-01')]
            connection.execute(f"INSERT OR REPLACE INTO user_item VALUES (?,?,?)", values)

            transaction.commit()


@pytest.mark.usefixtures("setup_db")
def test_user_info_exist(database):
    user = database.get_user_info('admin')
    assert user


@pytest.mark.usefixtures("setup_db")
def test_user_info_doesnt_exist(database):
    with pytest.raises(erros.UserDoesNotExist):
        user = database.get_user_info('test')


@pytest.mark.usefixtures("setup_db")
def test_track_info_single(database):
    track = database.get_track_info([0])
    assert len(track) == 1


@pytest.mark.usefixtures("setup_db")
def test_track_info_multiple(database):
    ans = database.get_track_info([0, 2])
    assert type(ans) == pd.DataFrame
    assert len(ans) == 1


@pytest.mark.usefixtures("setup_db")
def test_track_info_doesnt_exist(database):
    ans = database.get_track_info([1])
    assert type(ans) == pd.DataFrame
    assert len(ans) == 1


@pytest.mark.usefixtures("setup_db")
def test_user_item(database):
    ans = database.get_user_item()
    assert type(ans) == pd.DataFrame
    assert len(ans) == 2


@pytest.mark.usefixtures("setup_db")
def test_save_prediction(database):
    database.save_prediction(1, [[x for x in 'prediction'], []])

    with database.engine.connect() as connection:
        result = connection.execute("Select * from prediction").fetchall()

    assert len(result) == 1
    assert result[0][1] == 'p;r;e;d;i;c;t;i;o;n'
