import pandas as pd
import implicit
from scipy.sparse import coo_matrix, csr_matrix
import numpy as np
import pickle
from typing import Tuple, List


class als_model:
    """
    Als model based on implicit module
    Class model wrapper
    """

    def __init__(self, factors: int = 40, iterations: int = 30):
        self.track_list = None  # dict to recover track info from id
        self.data_test = None  # test_data DataFrame
        self.data_train = None  # train_data csr_matrix
        self.model_music = None  # als_implicit model
        self.factors = factors  # number of factors for model matrix
        self.iterations = iterations  # number of training iteration

    def train(self, train: pd.DataFrame, test: pd.DataFrame) -> None:
        """
        Train model
        :param train: DataFrame train dataset
        :param test: DataFrame test datatset
        """
        self.data_train = self._df_to_vect(train)  # create csr matrix

        self.track_list = self._track_df(train, test)
        self.data_test = self._test_df(test)

        self.model_music = implicit.als.AlternatingLeastSquares(factors=self.factors,
                                                                iterations=self.iterations,
                                                                num_threads=1
                                                                )
        self.model_music.fit(self.data_train.tocsr())

    def score(self) -> dict:
        """
        Calculate score p@k50 et AUC
        :return: dict of p@k and auc scores
        """
        # todo link with metrics
        return {}

    def recommend(self, user_id: int, nb_tracks: int = 10) -> Tuple[List[int], List[float]]:
        """
        Recommend n tracks for user id
        :param user_id: int user id
        :param nb_tracks: number of recommendations
        :return:
        """
        recommendation = self.model_music.recommend(userid=user_id,
                                                    user_items=self.data_train.tocsr()[user_id],
                                                    filter_already_liked_items=False,
                                                    N=nb_tracks)
        return recommendation

    def save(self, path: str = 'model/') -> None:
        """
        Save model in binary dump file in .mld format
        :param path: path to model folder
        """
        if self.model_music:
            with open(path + 'model_als.mdl', 'wb') as file:
                pickle.dump((self.model_music, self.data_train, self.data_test, self.track_list), file)

    def load(self, file_path: str = 'model/model_als.mdl') -> None:
        """
        load model from .mld file
        :param file_path: path to model file
        """
        with open(file_path, 'rb') as file:
            self.model_music, self.data_train, self.data_test, self.track_list = pickle.load(file)

    @staticmethod
    def _df_to_vect(df: pd.DataFrame) -> coo_matrix:
        """
        Create sparce matrix for model with
        :param df: DataFrame af dataset
        :return: COO Matrix (weight, (item, user)
        """

        df_gb = df.groupby(['user_id', 'track_id']).mean(numeric_only=True).reset_index()

        item = np.array(df_gb[['track_id']].values).T[0]
        user = np.array(df_gb[['user_id']].values).T[0]
        weight = np.array(df_gb[['rating']].values).T[0]

        mat_music = coo_matrix((weight, (item, user)))
        return mat_music.T

    @staticmethod
    def _track_df(df_train: pd.DataFrame, df_test: pd.DataFrame) -> pd.DataFrame:
        """
        Create a df with all track info
        :param df_train: df training data
        :param df_test: df test data
        :return: df with [track_id, artist_id, track_name, artist_name]
        """
        df = pd.concat([df_train, df_test])
        df = df.groupby('track_id').first().reset_index()
        return df.drop(columns=['user_id', 'time_stamp', 'rating'])

    @staticmethod
    def _test_df(df_test: pd.DataFrame) -> pd.DataFrame:
        """
        Reduce test data to user_id vs track_id
        :param df_test: df test_data
        :return: df with [user_id, track_id, nb_event]
        """
        df = df_test.groupby(['user_id', 'track_id']).size().reset_index(name='nb_event')
        df = df[['user_id', 'track_id', 'nb_event']]
        return df
