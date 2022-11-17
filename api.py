from fastapi import FastAPI, Header, HTTPException
from model import als_model
from train import train_model
import dotenv
from utils import track_id_to_info
from schemas import RecommendationRequest, RecommendationResult

dotenv.load_dotenv()

api = FastAPI(title="Pytune music recommender API",
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
    418: {"description": "I'm a tea pot"},
}

''' Set up and load als model'''
model = als_model()
model.load()


@api.get('/', name='Api test', tags=['home'])
async def get_index() -> dict:
    """
    Route to test if api is running\n
    :return: "running if alive"
    """
    return {'Api status': 'running'}


@api.post('/recommendation', name='music recommendations', tags=['recommendation'])
async def post_recommendations(request: RecommendationRequest):
    """
    Rerun N track id to listen to
    :return: List[track_id]
    """
    global model
    recommendations = model.recommend(user_id=request.user_id,
                                      nb_tracks=request.N_track,
                                      filter=request.filter_already_liked
                                      )
    result = track_id_to_info(recommendations, model.track_list)

    return {'Recommendations': result}


@api.get('/model/reload', name='reload model', tags=['admin'])
async def get_reload_model():
    """
    Reload model
    :return: List[track_id]
    """
    global model
    model.load()
    return {'status': 'model reloaded'}


@api.get('/model/train', name='train model', tags=['admin'])
async def get_train_model():
    """
    Reload model
    :return: List[track_id]
    """
    train_model()
    return {'status': 'model reloaded'}