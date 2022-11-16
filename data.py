import numpy as np
import pandas as pd
import datetime
import os
from typing import Tuple
from scipy.sparse import coo_matrix, csr_matrix
from implicit.nearest_neighbours import bm25_weight
from implicit import evaluation


def load_data() -> Tuple[pd.DataFrame, Tuple[csr_matrix, csr_matrix]]:
    """
    Load data from dataset, score tracks and return coo_matrix for model training
    :return:
    """
    df = load_df()
    df_track = track_df(df)
    df = track_score(df)
    mat_train, mat_test = train_test_split(df)
    return df_track, (mat_train, mat_test)


def load_df(date: datetime.date = datetime.datetime.now()) -> pd.DataFrame:
    """
    load dataset.csv file and filter by date
    :param date: latest date allowed
    :return: filtered df
    """

    df = pd.read_csv(os.getenv('DATA_FILE'), index_col=0)

    # todo refactor fake user and redo df
    folder = os.getenv('FAKE_USER_FOLDER')
    files = os.listdir(folder)

    for file in files:
        df_temp = pd.read_csv(f'{folder}{file}', index_col=0)
        df_temp['time_stamp'] = '2022-01-27 21:43:14'
        df = pd.concat([df, df_temp])

    df.dropna(inplace=True)
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])
    df = df[df['time_stamp'] < date]
    return df


def track_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate track score based on user listening history
    :param df: DataFrame with all listening event
    :return: DataFrame
    """
    df_track = df.groupby(['user_id', 'track_id']).size().reset_index(name='listening_count')
    return df_track


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


def track_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a df with all track info
    :param df: df training data
    :return: df with [track_id, artist_id, track_name, artist_name]
    """

    df = df.groupby('track_id').first().reset_index()
    return df.drop(columns=['user_id', 'time_stamp'])
