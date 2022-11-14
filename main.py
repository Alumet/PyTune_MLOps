from model import als_model
import dotenv
import data

dotenv.load_dotenv()

'''model = als_model(factors=10, iterations=5)

train, test = data.load_data()
model.train(train, test)
model.save()'''

model = als_model()
model.load()
reco = model.recommend(user_id=666)
print(model.track_list[model.track_list['track_id'].apply(lambda x: x in set(reco[0]))])


