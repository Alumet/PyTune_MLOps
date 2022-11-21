import numpy as np
import pandas as pd
import datetime
import os
from typing import Tuple, List
from scipy.sparse import coo_matrix, csr_matrix
from implicit.nearest_neighbours import bm25_weight
from implicit import evaluation

import sqlite3
import sqlalchemy
from utils import Singleton


@Singleton
class DataBase:
    def __init__(self):
        url = f'sqlite:///{os.getenv("DATA_BASE")}'
        self.engine = sqlalchemy.create_engine(url)

    def _request(self, request: str) -> list:
        with self.engine.connect() as connection:
            result = connection.execute(f"{request}")
            return result.fetchall()

    def _insert(self, request, values) -> None:
        with self.engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    ins = f"{request} VALUES ({','.join(['?' for i in values[0]])})"
                    connection.execute(ins, values)
                except Exception as e:
                    print(e)
                    transaction.rollback()
                else:
                    transaction.commit()

    def get_user_item(self, date: datetime.date = datetime.datetime.now()):
        request = f'select user_id, track_id from user_item where time_stamp <= "{date}"'
        ans = self._request(request)

        df = pd.DataFrame({'user_id': [x[0] for x in ans],
                           'track_id': [x[1] for x in ans]})

        df_track = df.groupby(['user_id', 'track_id']).size().reset_index(name='listening_count')

        return df_track

    def get_track_info(self, track_list: List[int]) -> pd.DataFrame:
        request = f'select * from track where id in {tuple(track_list)}'
        ans = self._request(request)

        df = pd.DataFrame({"track_id": [x[0] for x in ans],
                           "track_name": [x[1] for x in ans],
                           "artist_id": [x[2] for x in ans],
                           "artist_name": [x[3] for x in ans]
                           })
        return df

    def get_user_info(self, user_name: str) -> dict:
        request = f"select * from user where name = '{user_name}' limit 1"
        ans = self._request(request)[0]

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
        for rank, (track, score) in enumerate(zip(track_list, score_list)):
            values.append((user_id, int(track), float(score), rank+1, date))

        self._insert('INSERT OR REPLACE INTO prediction', values)

    def save_score(self, score: dict) -> None:
        date = datetime.datetime.now()
        values = []
        for key in score.keys():
            s = score[key]
            values.append((date, key, s['precision'], s['map'], s['ndcg'], s['auc']))

        self._insert('INSERT OR REPLACE INTO training', values)

    def add_event(self) -> None:
        # todo
        pass

    def add_user(self) -> None:
        # todo
        pass


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

    train, test = evaluation.train_test_split(mat, train_percentage=train_size)

    return train, test
