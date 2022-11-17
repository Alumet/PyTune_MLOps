from typing import List, Tuple
import pandas as pd


def track_id_to_info(recommendations: Tuple, track_df: pd.DataFrame) -> dict:
    """
    Create a dict with track info from track_id list
    :param recommendations:
    :param track_df:
    :return: dict with trac info(track_id, track_name, artist_name) and recommendation score
    """
    tracks, scores = recommendations
    result = {}

    for i, (track_id, score) in enumerate(zip(tracks, scores)):
        track = track_df[track_df['track_id'] == track_id].iloc[0]
        result[i + 1] = {"track_id": int(track_id),
                         "score": float(score),
                         "track_name": track['track_name'],
                         "artist_name": track['artist_name']}

    return result
