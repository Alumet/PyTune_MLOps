import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from typing import List, Tuple


class k_best:
    def __init__(self, user_tracks: set, recommended_tracks: list):
        self.user_tracks = user_tracks
        self.recommended_tracks = recommended_tracks

    def CG(self) -> int:
        return len(set(self.recommended_tracks).intersection(set(self.user_tracks)))

    def DCG(self) -> float:
        result = 0
        for i, id in enumerate(self.recommended_tracks):

            if id in self.user_tracks:
                result += 1 / np.log2(i + 2)

        return result

    def IDCG(self) -> float:
        a = self.CG()
        result = 0

        for i in range(a):
            result += 1 / np.log2(i + 2)

        return result

    def NDCG(self) -> float:
        if self.IDCG() != 0:
            result = self.DCG() / self.IDCG()
        else:
            result = 0

        return result

    def P_at_k(self) -> float:
        return self.CG() / len(self.recommended_tracks)

    def __str__(self) -> str:
        result = 'K_best ressults: \n'
        result += f'CG = {self.CG()}\n'
        result += f'DCG = {self.DCG()}\n'
        result += f'NDCG = {self.NDCG()}\n'
        result += f'P@K = {self.P_at_k()}\n'

        return result


def auc_score(y_true: List[int], ratings: List[float], thresholds: np.array = np.linspace(-0.25, 1, 26)) \
        -> Tuple[np.array, np.array]:
    """

    :param thresholds:
    :param ratings:
    :param y_true:
    :return:
    """

    roc_auc = list()

    for threshold in thresholds:
        y_pred = [1 if x > threshold else 0 for x in ratings]
        try:
            score = roc_auc_score(y_true, y_pred)
            roc_auc.append(score)
        except:
            roc_auc.append(0.5)

    return thresholds, np.array(roc_auc)

