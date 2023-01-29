import streamlit as st
import requests
from youtubesearchpython import VideosSearch

st.set_page_config(layout="wide")

if 'url' not in st.session_state:
    st.session_state.video_url = None


def log_is_valid() -> bool:
    x = requests.get('http://localhost:8000/login',
                     auth=(st.session_state.username, st.session_state.password))
    return x.status_code == 200


def add_user(user_name: str, pass_word: str) -> bool:
    data = {"user_name": user_name, "pass_word": pass_word, "is_admin": False}
    x = requests.post('http://localhost:8000/admin/user', json=data,
                      auth=('admin', 'admin'))

    return x.status_code == 200


def update_reco() -> None:
    if 'track_list' not in st.session_state:
        st.session_state.track_list = list()

    n_track = 20 - len(st.session_state.track_list)

    if n_track > 10:
        data = {"N_track": n_track, "filter_already_liked": True}
        x = requests.post('http://localhost:8000/recommendation', json=data,
                          auth=(st.session_state.username, st.session_state.password))
        reco = x.json()
    else:
        reco = dict()

    for key in reco:
        track = reco.get(key)
        if track not in st.session_state.track_list:
            st.session_state.track_list.append(reco.get(key))


def youtube_search(track: dict, id: int) -> None:
    st.session_state.playing = track

    txt = label = track.get('artist_name') + ' ' + track.get('track_name')
    videos_search = VideosSearch(txt, limit=1)

    url = videos_search.result().get('result')[0].get('link')
    length = videos_search.result().get('result')[0].get('duration')

    st.session_state.track_list.pop(id)
    st.session_state.video_url = url
    st.session_state.video_length = length


with st.sidebar:
    st.title('Pytune')

    st.write("Pytune is an music recommender system based on collaborative filtering")

    if 'logged' not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:
        st.subheader('Sign in')
        st.session_state.username = st.text_input('username', value='username', label_visibility="collapsed")
        st.session_state.password = st.text_input('password', value='password', label_visibility="collapsed",
                                                  type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button('Logg in'):
                if log_is_valid():
                    st.session_state.logged = True
                    st.experimental_rerun()

        with col2:
            if st.button('New user'):
                if add_user(st.session_state.username, st.session_state.password):
                    st.session_state.logged = True
                    st.experimental_rerun()

    else:
        st.write('User logged as: ', st.session_state.username)
        if st.button('Log out'):
            st.session_state.logged = False
            st.session_state.track_list = list()
            st.session_state.video_url = None
            st.experimental_rerun()


if st.session_state.logged:

    update_reco()

    col1, col2 = st.columns([4, 3])

    with col2:
        st.title('PLAYER')
        if not st.session_state.video_url:
            youtube_search(st.session_state.track_list[0], 0)
        st.video(st.session_state.video_url)
        st.write('Artist: ', st.session_state.playing.get("artist_name"))
        st.write('Track: ', st.session_state.playing.get("track_name"))
        st.write('Duration: ', st.session_state.video_length)

    with col1:
        st.title('SEARCH')
        search = st.text_input('search', value='', label_visibility="collapsed")
        if search != '':
            st.write('searching')
        st.title('RECOMMENDATION')
        for id, track in enumerate(st.session_state.track_list):
            label = track.get('artist_name') + ' --->  ' + track.get('track_name')
            st.button(label=label, on_click=youtube_search, args=[track, id], key=label)
            if id >= 5:
                break

else:
    st.title('Wellcome to PYTUNE! Please login!')
