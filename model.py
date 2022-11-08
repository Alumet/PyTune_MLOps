import pandas as pd

import pandas as ps
import implicit
from scipy.sparse import coo_matrix, csr_matrix
from typing import Tuple
import numpy as np
import pickle


class als_model:
    """

    """
    def __init__(self, factors: int = 40, iterations: int = 30):
        self.track_dict = None
        self.data_test = None
        self.data_train = None
        self.model_music = None
        self.factors = factors
        self.iterations = iterations

    def train(self, train: pd.DataFrame, test: pd.DataFrame) -> None:
        """

        :param train:
        :param test:
        :return:
        """
        self.data_train = self._df_to_vect(train)
        self.track_dict = train
        self.data_test = test

        self.model_music = implicit.als.AlternatingLeastSquares(factors=self.factors,
                                                                iterations=self.iterations,
                                                                num_threads=1
                                                                )
        self.model_music.fit(self.data_train)

    def save(self, path: str = 'model/'):
        """

        :param path:
        :return:
        """
        if self.model_music:
            with open(path + 'model_als.mdl', 'wb') as file:
                pickle.dump((self.model_music, self.data_train, self.data_test), file)

    def load(self, file_path: str = 'model/model_als.mdl'):
        """

        :param file_path:
        :return:
        """
        with open(file_path, 'rb') as file:
            self.model_music, self.data_train, self.data_test = pickle.load(file)

    @staticmethod
    def _df_to_vect(df: pd.DataFrame) -> csr_matrix:
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
        return mat_music.tocsr()
