from model import als_model
from train import train_model
import dotenv
from utils import track_id_to_info
from schemas import RecommendationRequest, User
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
with open('data/user_database.json', 'r') as file:
    users = json.load(file)


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """

    :param credentials:
    :return:
    """

    username = credentials.username

    db = DataBase.instance()
    user = db.get_user_info('test')

    if not (users.get(username)) or not (pwd_context.verify(credentials.password, user['hashed_password'])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user name or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get('/', name='Api test', tags=['home'], responses=responses)
async def get_index() -> dict:
    """
    Route to test if api is running
    :return: "running" if alive
    """
    return {'Api status': 'running'}


@app.post('/recommendation', name='music recommendations', tags=['recommendation'], responses=responses)
async def post_recommendations(request: RecommendationRequest, username: str = Depends(get_current_user)) -> dict:
    """
    Rerun N track id to listen to
    :return: List[track_id]
    """
    global model
    recommendations = model.recommend(user_id=request.user_id,
                                      nb_tracks=request.N_track,
                                      filter=request.filter_already_liked
                                      )

    db = DataBase.instance()
    track_df = db.get_track_info(recommendations[0])

    result = track_id_to_info(recommendations, track_df)

    return result


@app.get('/model/reload', name='reload model', tags=['admin'], responses=responses)
async def get_reload_model(username: str = Depends(get_current_user)) -> dict:
    """
    Reload model
    :return: status
    """
    if not users[username]['admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privilege",
            headers={"WWW-Authenticate": "Basic"},
        )

    global model
    model.load()
    return {'status': 'model reloaded'}


@app.get('/model/train', name='train model', tags=['admin'], responses=responses)
async def get_train_model(username: str = Depends(get_current_user)) -> dict:
    """
    Reload model
    :return: status
    """
    if not users[username]['admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privilege",
            headers={"WWW-Authenticate": "Basic"},
        )
    train_model()
    return {'status': 'model reloaded'}


@app.post('/user', name='add new user', tags=['admin'], responses=responses)
async def post_add_user(user_request: User, username: str = Depends(get_current_user)) -> dict:
    """
    Add a new user
    :return: status
    """
    if not users[username]['admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privilege",
            headers={"WWW-Authenticate": "Basic"},
        )

    if user_request.user_name not in users.keys():

        users[user_request.user_name] = {"username": user_request.user_name,
                                         "admin": user_request.is_admin,
                                         "hashed_password": pwd_context.hash(user_request.pass_word)}

        with open('data/user_database.json', 'w') as file:
            json.dump(users, file, indent=4, sort_keys=True)

    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user name already taken",
            headers={"WWW-Authenticate": "Basic"},
        )

    return {'status': 'user added'}
