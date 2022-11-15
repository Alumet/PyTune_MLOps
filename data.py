import pandas as pd
import datetime
import os
from typing import Tuple


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load data from dataset, score tracks and return coo_matrix for model training
    :return:
    """
    df = load_df()
    df = track_score(df)
    df_train, df_test = train_test_split(df)
    return df_train, df_test


def load_df(date: datetime.date = datetime.datetime.now()) -> pd.DataFrame:
    """
    load dataset.csv file and filter by date
    :param date: latest date allowed
    :return: filtered df
    """

    df = pd.read_csv(os.getenv('DATA_FILE'), index_col=0)

    # todo refactor fake user and redo df
    folder = os.getenv('FAKE_USER_folder')
    files = os.listdir(folder)

    for file in files:
        print(file)
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
    g = df_track.groupby('user_id')["listening_count"]
    min_, max_ = g.transform('min'), g.transform('max')
    df_track["listening_count_normalised"] = (df_track["listening_count"] - min_) / (max_ - min_) * 99
    df_track["listening_count_normalised"] = df_track["listening_count_normalised"].fillna(0.0).astype(int) + 1
    df_final_jg = df_track[["user_id", "track_id", "listening_count_normalised"]]
    df_final_jg = df_final_jg.rename(columns={"listening_count_normalised": "rating"})
    df_rating = pd.merge(
        df,
        df_final_jg,
        how="left",
        left_on=['user_id', 'track_id'],
        right_on=['user_id', 'track_id']
    )
    return df_rating


def train_test_split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cut dataset in sub train and test dataset.
    Test dataset equals last 2 days and train dataset equals to eventing older than 2 days
    :param df: DataFrame with listening events
    :return: df_train, df_test
    """
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])
    date = df['time_stamp'].max() - datetime.timedelta(days=2)

    df_test = df[df['time_stamp'] > date]
    df_train = df[df['time_stamp'] < date]

    return df_train, df_test


