from typing import List, Tuple
import pandas as pd


def track_id_to_info(recommendations: Tuple, track_df: pd.DataFrame) -> dict:
    tracks, scores = recommendations

    result = {}
    for i, (track_id, score) in enumerate(zip(tracks, scores)):
        track = track_df[track_df['track_id'] == track_id].iloc[0]
        result[i + 1] = {"track_id": int(track_id),
                         "score": float(score),
                         "track_name": track['track_name'],
                         "artist_name": track['artist_name']}

    return result


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)