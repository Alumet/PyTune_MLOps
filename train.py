import data
import implicit
from scipy.sparse import coo_matrix
from typing import Tuple


def train_model() -> Tuple[implicit.als, coo_matrix]:
    train, test = data.load_data()
    model_music = implicit.als.AlternatingLeastSquares(factors=40,
                                                       use_native=True,
                                                       use_cg=True,
                                                       calculate_training_loss=True,
                                                       num_threads=-1,
                                                       iterations=30)

    model_music.fit(train)

    return model_music, train
