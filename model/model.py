import implicit
from implicit.evaluation import ranking_metrics_at_k
from scipy.sparse import csr_matrix
import pickle
from typing import Tuple, List
import os
from utils import erros
import warnings


class als_model:
    """
    Als model based on implicit module
    Class model wrapper
    """

    def __init__(self, factors: int = 200, iterations: int = 30, alpha: float = 0.5):
        self.data_test = None  # test_data DataFrame
        self.data_train = None  # train_data DataFrame
        self.user_items = None  # train_data csr_matrix
        self.model_music = None  # als_implicit model
        self.factors = factors  # number of factors for model matrix
        self.iterations = iterations  # number of training iteration
        self.alpha = alpha

    def train(self, train: csr_matrix, test: csr_matrix) -> None:
        """
        Train model
        :param train: DataFrame train dataset
        :param test: DataFrame test datatset
        """
        self.user_items = train
        self.data_test = test

        self.model_music = implicit.als.AlternatingLeastSquares(factors=self.factors,
                                                                iterations=self.iterations,
                                                                alpha=self.alpha,
                                                                use_native=True,
                                                                calculate_training_loss=True,
                                                                num_threads=1,
                                                                random_state=42
                                                                )
        self.model_music.fit(self.user_items.tocsr())

    def score(self) -> dict:
        """
        Calculate score p@k50 et AUC
        :return: dict of p@k and auc scores
        """
        if self.model_music is None:
            raise erros.ModelNotTrained

        metrics = ranking_metrics_at_k(self.model_music,
                                       self.user_items,
                                       self.data_test,
                                       50,
                                       show_progress=False
                                       )
        result = {50: metrics}
        return result

    def recommend(self, user_id: int, nb_tracks: int = 10, filter: bool = False) -> Tuple[List[int], List[float]]:
        """
        Recommend n tracks for user id
        :param filter: filter already liked titles
        :param user_id: int user id
        :param nb_tracks: number of recommendations
        :return:
        """
        if self.model_music is None:
            raise erros.ModelNotTrained

        recommendation = self.model_music.recommend(userid=user_id,
                                                    user_items=self.user_items[user_id],
                                                    filter_already_liked_items=filter,
                                                    N=nb_tracks)
        return recommendation

    def similar_item(self, item_id: int, nb_tracks: int = 10) -> Tuple[List[int], List[float]]:
        """
        Recommend n track similar to item
        :param item_id: int track id
        :param nb_tracks: nb of track to return
        :return:
        """
        if self.model_music is None:
            raise erros.ModelNotTrained

        recommendation = self.model_music.similar_items(itemid=item_id,
                                                        item_users=self.user_items,
                                                        N=nb_tracks)
        return recommendation

    def rank_item(self, user_id: int, item_list: list):
        ranks = self.model_music.recommend(userid=user_id,
                                           user_items=self.user_items[user_id],
                                           filter_already_liked_items=False,
                                           items=item_list,
                                           N=len(item_list))
        return ranks

    def save(self, path: str = None) -> None:
        """
        Save model in binary dump file in .mld format
        :param path: path to model folder
        """
        if not path:
            path = os.getenv('MODEL_FOLDER')

        if self.model_music:
            with open(path + 'model_als.mdl', 'wb') as file:
                pickle.dump((self.model_music,
                             self.user_items,
                             self.data_test
                             ),
                            file)
        else:
            raise erros.ModelNotTrained

    def load(self, file_path: str = None) -> None:
        """
        load model from .mld file
        :param file_path: path to model file
        """
        if not file_path:
            file_path = os.getenv('PRODUCTION_MODEL')

        try:
            with open(file_path, 'rb') as file:
                self.model_music, self.user_items, self.data_test = pickle.load(file)
        except FileNotFoundError:
            warnings.warn(f'Model file "{file_path}" not found, blanc model loaded instead. Need to be trained')
        except ValueError:
            warnings.warn(f'Model file "{file_path}" not valid, blanc model loaded instead. Need to be trained')
        except TypeError:
            warnings.warn(f'Model file "{file_path}" not valid, blanc model loaded instead. Need to be trained')

        # todo test if elements are valid
