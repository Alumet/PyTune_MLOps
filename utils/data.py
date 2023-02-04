import numpy as np
import pandas as pd
import datetime
import os
from typing import Tuple, List
from scipy.sparse import coo_matrix, csr_matrix
from implicit.nearest_neighbours import bm25_weight
from implicit import evaluation
from utils.schemas import User, Event
from .erros import UserAlreadyExist, TrackDoesNotExist, UserDoesNotExist, BadSearch

import sqlalchemy
from utils.utils import Singleton


@Singleton
class DataBase:
    def __init__(self):
        self.url = os.getenv("DATA_BASE")
        self.engine = sqlalchemy.create_engine(self.url)

        # todo : find a better way
        if 'mysql' in self.url:
            self.char = '%s'
        else:
            self.char = '?'

    def _request(self, request: str) -> list:
        with self.engine.connect() as connection:
            result = connection.execute(f"{request}")
            return result.fetchall()

    def _insert(self, request, values) -> None:
        with self.engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    ins = f"{request} VALUES ({','.join([self.char for i in values[0]])})"
                    connection.execute(ins, values)
                except Exception as e:
                    transaction.rollback()
                    raise e
                else:
                    transaction.commit()

    def search_item(self, txt: str) -> pd.DataFrame:

        if '"' in txt:
            # Avoid sql injection
            raise BadSearch

        request = f'Select * from track where title LIKE "%%{txt}%%" LIMIT 20'
        ans = self._request(request)

        df = pd.DataFrame({"track_id": [x[0] for x in ans],
                           "track_name": [x[1] for x in ans],
                           "artist_id": [x[2] for x in ans],
                           "artist_name": [x[3] for x in ans]
                           })
        return df

    def get_user_item(self, date: datetime.date = datetime.datetime.now()):
        request = f'select user_id, track_id from user_item where time_stamp <= "{date}"'
        ans = self._request(request)

        df = pd.DataFrame({'user_id': [x[0] for x in ans],
                           'track_id': [x[1] for x in ans]})

        df_track = df.groupby(['user_id', 'track_id']).size().reset_index(name='listening_count')

        return df_track

    def get_track_info(self, track_list: List[int]) -> pd.DataFrame:

        if len(track_list) == 1:
            r = f'({track_list[0]})'
        else:
            r = tuple(track_list)

        request = f'select * from track where id in {r}'
        ans = self._request(request)

        df = pd.DataFrame({"track_id": [x[0] for x in ans],
                           "track_name": [x[1] for x in ans],
                           "artist_id": [x[2] for x in ans],
                           "artist_name": [x[3] for x in ans]
                           })
        return df

    def get_user_info(self, user_name: str) -> dict:
        request = f"select * from user where name = '{user_name}' limit 1"
        ans = self._request(request)

        if len(ans) == 0:
            raise UserDoesNotExist
        else:
            ans = ans[0]

        user = {'id': ans[0],
                'username': ans[1],
                'admin': ans[2] == 1,
                'hashed_password': ans[3],
                }
        return user

    def save_prediction(self, user_id: int, recommendation: list) -> None:
        date = datetime.datetime.now()
        values = []

        track_list, score_list = recommendation
        track_list = ';'.join([str(x) for x in track_list])
        values.append((user_id, track_list, date))

        self._insert('INSERT INTO prediction', values)

    def save_score(self, score: dict) -> None:
        date = datetime.datetime.now()
        values = []
        for key in score.keys():
            s = score[key]
            values.append((date, key, s['precision'], s['map'], s['ndcg'], s['auc']))

        self._insert('INSERT INTO training', values)

    def add_event(self, user_id: int, event: Event) -> None:

        if len(self._request(f"Select * from track where id='{event.track_id}'")) != 0:
            request = 'INSERT INTO user_item'
            date = datetime.datetime.now()
            values = [(user_id, event.track_id, date)]
            self._insert(request, values)
        else:
            raise TrackDoesNotExist

    def add_user(self, user: User) -> None:

        id = self._request('Select max(id) from user')[0][0] + 1

        if len(self._request(f"Select * from user where name = '{user.user_name}'")) == 0:
            values = [(id, user.user_name, user.is_admin, user.pass_word)]
            print(user.pass_word, values)
            self._insert('INSERT INTO user', values)
        else:
            raise UserAlreadyExist


def load_data() -> Tuple[csr_matrix, csr_matrix]:
    """
    Load data from dataset, score tracks and return coo_matrix for model training
    :return:
    """
    db = DataBase.instance()
    df = db.get_user_item()
    mat_train, mat_test = train_test_split(df)
    return mat_train, mat_test


def train_test_split(df: pd.DataFrame, train_size: float = 0.8) -> Tuple[csr_matrix, csr_matrix]:
    """
    Cut dataset in sub train and test dataset.
    :param train_size: train dataset size
    :param df: DataFrame with listening events
    :return: df_train, df_test
    """
    df_gb = df.groupby(['user_id', 'track_id']).mean(numeric_only=True).reset_index()

    item = np.array(df_gb[['track_id']].values).T[0]
    user = np.array(df_gb[['user_id']].values).T[0]
    weight = np.array(df_gb[['listening_count']].values).T[0]

    mat = coo_matrix((weight, (item, user)))
    mat = bm25_weight(mat, K1=100, B=0.8)
    mat = mat.T.tocsr()

    train, test = evaluation.train_test_split(mat, train_percentage=train_size, random_state=42)

    return train, test
