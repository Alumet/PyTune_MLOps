from model import als_model
import dotenv
from train import train_model
from data import DataBase
dotenv.load_dotenv()

#train_model()

"""model = als_model()
model.load()
print(model.score())

for user in [1001, 1002, 1003, 1004, 1005]:
    reco = model.recommend(user_id=user)
    a = model.track_list[model.track_list['track_id'].apply(lambda x: x in set(reco[0]))]
    print(a[['artist_name', 'track_name']])"""

db = DataBase.instance()
print(db.get_user_info('user_jazz'))

model = als_model()
model.load()
reco = model.recommend(user_id=0, nb_tracks=10)
print(reco)
'''
db.save_prediction(user_id=1005, recommendation=reco)'''

