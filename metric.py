import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


class k_best:
    def __init__(self, user_tracks, recommended_tracks):
        self.user_tracks = user_tracks
        self.recommended_tracks = recommended_tracks

    def CG(self):
        return len(set(self.recommended_tracks).intersection(set(self.user_tracks)))

    def DCG(self):
        result = 0
        for i, id in enumerate(self.recommended_tracks):

            if id in self.user_tracks:
                result += 1 / np.log2(i + 2)

        return result

    def IDCG(self):
        a = self.CG()
        result = 0

        for i in range(a):
            result += 1 / np.log2(i + 2)

        return result

    def NDCG(self):
        if self.IDCG() != 0:
            result = self.DCG() / self.IDCG()
        else:
            result = 0

        return result

    def P_at_k(self):
        return self.CG() / len(self.recommended_tracks)

    def __str__(self):
        result = 'K_best ressults: \n'
        result += f'CG = {self.CG()}\n'
        result += f'DCG = {self.DCG()}\n'
        result += f'NDCG = {self.NDCG()}\n'
        result += f'P@K = {self.P_at_k()}\n'

        return result


def auc_score(df_train, df_test, model, mat, seuils=[0]):
    ids = df_train['user_id'].unique()

    auc_train_all = dict()
    auc_test_all = dict()

    item = []  # todo replace

    for user in ids:
        a = model.rank_items(user, mat.tocsr().T, list(set(item)))

        id = [x[0] for x in a]
        score = [x[1] for x in a]

        df_temp = pd.DataFrame({'id': id, 'score': score})

        user_tracks_train = set([x for x in df_train[df_train['user_id'] == user]['track_id'].unique()])
        user_tracks_test = set([x for x in df_test[df_test['user_id'] == user]['track_id'].unique()])

        df_temp['train'] = df_temp['id'].apply(lambda x: 1 if x in user_tracks_train else 0)
        df_temp['test'] = df_temp['id'].apply(lambda x: 1 if x in user_tracks_test else 0)

        y_true_test = df_temp['test']
        y_true_train = df_temp['train']

        for s in seuils:

            try:

                y_pred = [1 if x > s else 0 for x in df_temp['score']]

                auc_test = roc_auc_score(y_true_test, y_pred)
                auc_train = roc_auc_score(y_true_train, y_pred)

                try:
                    auc_train_all[s].append(auc_train)
                    auc_test_all[s].append(auc_test)
                except:
                    auc_train_all[s] = [auc_train]
                    auc_test_all[s] = [auc_test]

            except:
                pass

    return auc_train_all, auc_test_all
