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


with st.sidebar:
    st.title('Pytune')

    if 'logged' not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:
        st.subheader('Sign in')
        st.session_state.username = st.text_input('username', value='username', label_visibility="collapsed")
        st.session_state.password = st.text_input('password', value='password', label_visibility="collapsed", type="password")

        if st.button('Logg in'):
            if log_is_valid():
                st.session_state.logged = True
                st.experimental_rerun()
            else:
                st.experimental_rerun()
                st.write('Invalid Credentials !')

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
