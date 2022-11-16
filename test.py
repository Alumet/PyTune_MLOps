import os

import data
import model
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, csr_matrix
import erros
import pytest
import pickle

""" data.py test """


def test_data_track_score_df():
    df = pd.DataFrame({'user_id': [1, 1, 2, 2, 3],
                       'track_id': [1, 2, 1, 1, 2]})

    df_score = data.track_score(df)
    assert type(df_score) == pd.DataFrame
    assert list(df_score['listening_count'].values) == [1, 1, 2, 1]


def test_data_train_test_split():
    df = pd.DataFrame({'user_id': [1, 1, 2, 3],
                       'track_id': [1, 2, 1, 2],
                       'listening_count': [1, 1, 2, 1]})

    train, test = data.train_test_split(df)

    assert type(train) == csr_matrix
    assert type(test) == csr_matrix


def test_data_track_df():
    df = pd.DataFrame({'user_id': [1, 1, 2, 3],
                       'track_id': [1, 2, 1, 2],
                       'time_stamp': [1, 1, 2, 1]})

    df_track = data.track_df(df)

    assert type(df_track) == pd.DataFrame
    assert df_track.shape[0] == 2


""" model.py test """


def test_model():
    m = model.als_model(factors=10,
                        iterations=20,
                        alpha=30)
    assert m.factors == 10
    assert m.iterations == 20
    assert m.alpha == 30


def test_model_train():
    m = model.als_model(factors=10,
                        iterations=1,
                        alpha=1)

    train = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))
    test = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))

    m.train(train, test)

    assert m.model_music is not None


def test_model_score_untrained():
    m = model.als_model()
    with pytest.raises(erros.ModelNotTrained):
        m.score()


def test_model_score_trained():
    m = model.als_model(factors=10,
                        iterations=1,
                        alpha=1)

    train = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))
    test = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))

    m.train(train, test)

    score = m.score()
    assert type(score) == dict


def test_model_recommend_trained():
    m = model.als_model(factors=10,
                        iterations=1,
                        alpha=1)

    train = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))
    test = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))

    m.train(train, test)

    reco = m.recommend(user_id=1, nb_tracks=2)

    assert type(reco) == tuple
    assert len(reco) == 2
    assert type(reco[0]) == np.ndarray
    assert type(reco[1]) == np.ndarray


def test_model_recommend_untrained():
    m = model.als_model()
    with pytest.raises(erros.ModelNotTrained):
        reco = m.recommend(user_id=1, nb_tracks=2)


def test_model_save_untrained(tmpdir):
    m = model.als_model()
    path = f'{tmpdir}\\'
    with pytest.raises(erros.ModelNotTrained):
        m.save(path)


def test_model_save_trained(tmpdir):
    m = model.als_model(factors=10,
                        iterations=1,
                        alpha=1)

    train = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))
    test = csr_matrix(([1, 1, 1, 1], ([1, 2, 1, 2], [1, 1, 2, 3])))

    m.train(train, test)

    path = f'{tmpdir}\\'
    m.save(path=path)
    assert 'model_als.mdl' in os.listdir(path)


def test_model_load(tmpdir):
    path = f'{tmpdir}\\'
    with open(path + 'model_als.mdl', 'wb') as file:
        pickle.dump(('model',
                     'mat_train',
                     'mat_test',
                     'track_list'), file)

    m = model.als_model()
    m.load(path + 'model_als.mdl')
