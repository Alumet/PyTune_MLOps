import streamlit as st
import requests
from youtubesearchpython import VideosSearch
import dotenv
import os
from random import shuffle
from typing import Tuple, List

# Load .env
dotenv.load_dotenv()
api_url = os.getenv('API_URL')

st.set_page_config(layout="wide")


# Set Up Session
def set_session():
    if 'video_url' not in st.session_state:
        st.session_state.video_url = None
    if 'search' not in st.session_state:
        st.session_state.search = None
    if 'listened_tracks' not in st.session_state:
        st.session_state.listened_tracks = list()
    if 'logged' not in st.session_state:
        st.session_state.logged = False
    if 'warning' not in st.session_state:
        st.session_state.warning = ''
    if 'track_list' not in st.session_state:
        st.session_state.track_list = list()


def reset_session():
    st.session_state.logged = False
    st.session_state.track_list = list()
    st.session_state.video_url = None
    st.session_state.listened_tracks = list()


set_session()


# Class to communicate with API
class API:

    @staticmethod
    def log_is_valid() -> bool:
        x = requests.get(f'{api_url}/login',
                         auth=(st.session_state.username, st.session_state.password))
        return x.status_code == 200

    @staticmethod
    def add_user(user_name: str, pass_word: str) -> bool:
        data = {"user_name": user_name, "pass_word": pass_word, "is_admin": False}
        x = requests.post(f'{api_url}/admin/user', json=data,
                          auth=('admin', 'admin'))

        return x.status_code == 200

    @staticmethod
    def reco_model(n_track: int) -> List:
        data = {"N_track": n_track, "filter_already_liked": True}
        x = requests.post(f'{api_url}/recommendation', json=data,
                          auth=(st.session_state.username, st.session_state.password))
        if x.status_code == 200:
            reco = x.json()
            return [reco.get(key) for key in reco]
        else:
            return []

    @staticmethod
    def reco_similar() -> List:
        reco = list()
        for i, id in enumerate(st.session_state.listened_tracks[::-1]):
            data = {"N_track": 2, 'track_id': id}
            x = requests.post(f'{api_url}/similar', json=data,
                              auth=(st.session_state.username, st.session_state.password))
            if x.status_code == 200:
                sub_reco = x.json()
            else:
                sub_reco = []

            if i > 2:
                break

            reco += [sub_reco.get(key) for key in sub_reco]
            shuffle(reco)

        return reco

    @staticmethod
    def add_event(track) -> None:
        data = {"track_id": track.get('track_id')}
        x = requests.post(f'{api_url}/event', json=data,
                          auth=(st.session_state.username, st.session_state.password))

    @staticmethod
    def track_search(txt):
        data = {"search": txt}
        x = requests.post(f'{api_url}/search', params=data,
                          auth=(st.session_state.username, st.session_state.password))
        ans = x.json()

        st.session_state.search_result = [ans.get(key) for key in ans]


def youtube_search(txt: str) -> Tuple[str, str]:
    videos_search = VideosSearch(txt, limit=1)

    url = videos_search.result().get('result')[0].get('link')
    length = videos_search.result().get('result')[0].get('duration')

    return url, length


def play(track: dict, id: int, remove: bool = False) -> None:
    st.session_state.playing = track

    txt = track.get('artist_name') + ' ' + track.get('track_name')
    url, length = youtube_search(txt)

    if remove:
        st.session_state.track_list.pop(id)

    st.session_state.video_url = url
    st.session_state.video_length = length

    API.add_event(track)
    st.session_state.listened_tracks.append(track.get('track_id'))


def update_reco() -> None:
    reco = API.reco_model(50)

    if reco == [] and len(st.session_state.listened_tracks) > 0:
        reco = API.reco_similar()

    for track in reco.copy():
        if track.get('track_id') in st.session_state.listened_tracks:
            reco.remove(track)

    st.session_state.track_list = reco

    st.session_state.listened_tracks = st.session_state.listened_tracks[:20]


def login_widget():
    st.subheader('Sign in')

    st.session_state.username = st.text_input('username', value='username', label_visibility="collapsed")
    st.session_state.password = st.text_input('password', value='password', label_visibility="collapsed",
                                              type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Logg in'):
            if API.log_is_valid():
                st.session_state.logged = True
                st.experimental_rerun()
                st.session_state.warning = ""
            else:
                st.session_state.warning = "!! Invalid username or password !!"

    with col2:
        if st.button('New user'):
            if API.add_user(st.session_state.username, st.session_state.password):
                st.session_state.logged = True
                st.experimental_rerun()
                st.session_state.warning = ""
            else:
                st.session_state.warning = " !! Username already used, chose another one !!"

    st.write(st.session_state.warning)


def reco_widget():
    update_reco()

    col1, col2 = st.columns([4, 3])

    with col2:
        st.title('PLAYER')

        if not st.session_state.video_url and st.session_state.track_list != []:
            play(st.session_state.track_list[0], 0, True)

        if st.session_state.video_url:
            st.video(st.session_state.video_url)
            st.write('Artist: ', st.session_state.playing.get("artist_name"))
            st.write('Track: ', st.session_state.playing.get("track_name"))
            st.write('Duration: ', st.session_state.video_length)

    with col1:
        st.title('SEARCH')
        search = st.text_input('search', value='', label_visibility="collapsed")

        if search != '':
            if search != st.session_state.search:
                API.track_search(search)
                st.session_state.search = search
            with st.expander('Search result'):
                for id, track in enumerate(st.session_state.search_result):
                    label = track.get('artist_name') + ' --->  ' + track.get('track_name')
                    st.button(label=label, on_click=play, args=[track, id], key=label + '_search')
                    if id >= 10:
                        break

        st.title('RECOMMENDATION')
        if not st.session_state.track_list:
            st.write('No recommendation available yet !')
            st.write('   1 - search for track')
            st.write('   2 - listen to one track')
            st.write('   3 - basic recommendation will be available')
            st.write('   4 - personalised recommendation will be available model retrain')

        for id, track in enumerate(st.session_state.track_list):
            label = track.get('artist_name') + ' --->  ' + track.get('track_name')
            st.button(label=label, on_click=play, args=[track, id, True], key=label + '_reco')
            if id >= 5:
                break


if __name__ == "__main__":

    with st.sidebar:
        st.title('Pytune')

        if not st.session_state.logged:
            login_widget()

        else:
            st.write('User logged as: ', st.session_state.username)
            if st.button('Log out'):
                reset_session()
                st.experimental_rerun()

    if st.session_state.logged:
        reco_widget()
    else:
        st.title('Wellcome to PYTUNE! Please login!')
        st.write("Pytune is an music recommender system based on collaborative filtering")
