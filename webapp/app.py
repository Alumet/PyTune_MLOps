import streamlit as st
import requests


def log_is_valid():
    x = requests.get('http://localhost:8000/login',
                      auth=(st.session_state.username, st.session_state.password))
    return x.status_code == 200


def add_user(user_name, pass_word):
    data = {"user_name": user_name, "pass_word": pass_word, "is_admin": False}
    x = requests.post('http://localhost:8000/admin/user', json=data,
                      auth=('admin', 'admin'))

    return x.status_code == 200


def get_reco():
    data = {"N_track": 10, "filter_already_liked": False}
    x = requests.post('http://localhost:8000/recommendation', json=data,
                      auth=(st.session_state.username, st.session_state.password))

    return x.json()


with st.sidebar:
    st.title('Pytune')

    st.write("Pytune is an music recommender system based on collaborative filtering")

    if 'logged' not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:
        st.subheader('Sign in')
        st.session_state.username = st.text_input('username', value='username', label_visibility="collapsed")
        st.session_state.password = st.text_input('password', value='password', label_visibility="collapsed", type="password")

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
            st.experimental_rerun()


if st.session_state.logged:
    st.title('RECOMMENDATION')
    st.write(get_reco())
else:
    st.title('Wellcome to PYTUNE! Please login!')

