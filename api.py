from model import als_model
from train import train_model
import dotenv
from utils import track_id_to_info
from schemas import UserRecommendationRequest, AdminRecommendationRequest, User
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import json
from data import DataBase

dotenv.load_dotenv()

app = FastAPI(title="Pytune music recommender API",
              description="Get music recommendation from Pytune implicit collaborative filtering model",
              version="1.0.0",
              openapi_tags=[{'name': 'home',
                             'description': 'endpoints made for api test'
                             },
                            {'name': 'recommendation',
                             'description': 'recommender endpoints'
                             },
                            {'name': 'admin',
                             'description': 'admin area'
                             }
                            ]
              )

responses = {
    200: {"description": "OK"},
    404: {"description": "Item not found"},
    401: {"description": "Unauthorised"},
    403: {"description": "Not enough privileges"},
    409: {"description": "Conflict"},
}

''' Set up and load als model'''
model = als_model()
model.load()

''' Set up Security'''
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """

    :param credentials:
    :return:
    """

    username = credentials.username

    db = DataBase.instance()
    user = db.get_user_info(username)
    print(pwd_context.verify(credentials.password, user['hashed_password']))

    if not (user['username'] == username) or not (pwd_context.verify(credentials.password, user['hashed_password'])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user name or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


@app.get('/', name='Api test', tags=['home'], responses=responses)
async def get_index() -> dict:
    """
    Route to test if api is running
    :return: "running" if alive
    """
    return {'Api status': 'running'}


@app.post('/recommendation', name='music recommendations', tags=['recommendation'], responses=responses)
async def post_recommendations(request: UserRecommendationRequest, user: dict = Depends(get_current_user)) -> dict:
    """
    Rerun N track id to listen to
    :return: List[track_id]
    """
    global model
    try:
        recommendations = model.recommend(user_id=user['id'],
                                          nb_tracks=request.N_track,
                                          filter=request.filter_already_liked
                                          )
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User need to add listening events and/ or model needs to be retrained",
            headers={"WWW-Authenticate": "Basic"},
        )

    db = DataBase.instance()
    track_df = db.get_track_info(recommendations[0])

    result = track_id_to_info(recommendations, track_df)

    return result


@app.get('/model/reload', name='reload model', tags=['admin'], responses=responses)
async def get_reload_model(user: dict = Depends(get_current_user)) -> dict:
    """
    Reload model
    :return: status
    """
    if not user['admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privilege",
            headers={"WWW-Authenticate": "Basic"},
        )

    global model
    model.load()
    return {'status': 'model reloaded'}


@app.get('/model/train', name='train model', tags=['admin'], responses=responses)
async def get_train_model(user: dict = Depends(get_current_user)) -> dict:
    """
    Reload model
    :return: status
    """
    if not user['admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privilege",
            headers={"WWW-Authenticate": "Basic"},
        )
    train_model()
    return {'status': 'model reloaded'}


@app.post('/admin/user', name='add new user', tags=['admin'], responses=responses)
async def post_add_user(user_request: User, user: dict = Depends(get_current_user)) -> dict:
    """
    Add a new user
    :return: status
    """
    if not user['admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privilege",
            headers={"WWW-Authenticate": "Basic"},
        )

    if user_request.user_name not in []:

        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user name already taken",
            headers={"WWW-Authenticate": "Basic"},
        )

    return {'status': 'user added'}


@app.post('/admin/recommendation', name='music recommendations', tags=['admin'], responses=responses)
async def post_recommendations_admin(request: AdminRecommendationRequest, user: dict = Depends(get_current_user)) -> dict:
    """
    Rerun N track id to listen to for specific user_id
    :return: List[track_id]
    """
    global model
    try:
        recommendations = model.recommend(user_id=request.user_id,
                                          nb_tracks=request.N_track,
                                          filter=request.filter_already_liked
                                          )
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user unknown by model, create user and/or add listening events",
            headers={"WWW-Authenticate": "Basic"},
        )

    db = DataBase.instance()
    track_df = db.get_track_info(recommendations[0])

    result = track_id_to_info(recommendations, track_df)

    return result
