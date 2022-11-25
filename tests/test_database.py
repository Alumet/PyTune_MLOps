from utils import data, erros

import pandas as pd
from scipy.sparse import csr_matrix
import pytest

from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData, Boolean, Date, Float

from utils.schemas import Event, User

""" test DataBase"""


def test_database(monkeypatch):
    monkeypatch.setenv("DATA_BASE", ":memory:")
    db = data.DataBase.instance()
    assert db


@pytest.fixture
def database(monkeypatch):
    monkeypatch.setenv("DATA_BASE", ":memory:")
    db = data.DataBase.instance()
    yield db

    with db.engine.connect() as connection:
        for table in ['training', 'prediction', 'user_item', 'track', 'artist', 'user']:
            with connection.begin() as transaction:
                connection.execute(f"DROP TABLE {table}")
                try:
                    transaction.commit()
                except Exception:
                    transaction.rollback()


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


@pytest.mark.usefixtures("setup_db")
def test_add_event(database):
    event = Event
    event.track_id = 1
    database.add_event(user_id=0, event=event)

    with database.engine.connect() as connection:
        result = connection.execute("Select * from user_item where user_id=0").fetchall()

    assert len(result) == 3


@pytest.mark.usefixtures("setup_db")
def test_add_event_track_doesnt_exist(database):
    event = Event
    event.track_id = 10
    with pytest.raises(erros.TrackDoesNotExist):
        database.add_event(user_id=0, event=event)


@pytest.mark.usefixtures("setup_db")
def test_add_user(database):
    user = User
    user.user_name = 'test'
    user.pass_word = 'arezaze'
    user.is_admin = False

    database.add_user(user=user)

    with database.engine.connect() as connection:
        result = connection.execute("Select * from user where name='test'").fetchall()

    assert len(result) == 1


@pytest.mark.usefixtures("setup_db")
def test_add_user_not_valid(database):
    user = User
    user.user_name = 'admin'
    user.pass_word = 'arezaze'
    user.is_admin = False

    with pytest.raises(erros.UserAlreadyExist):
        database.add_user(user=user)


""" test data prep"""


def test_train_test_split():
    df = pd.DataFrame({'track_id': [1, 1, 1, 2, 3],
                       'user_id': [1, 1, 2, 2, 1],
                       'listening_count': [3, 3, 1, 4, 1]})

    result = data.train_test_split(df)
    assert len(result) == 2
    train, test = result
    assert type(train) == csr_matrix
    assert type(test) == csr_matrix
