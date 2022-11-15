from model import als_model
import dotenv
import data

dotenv.load_dotenv()

"""model = als_model(factors=150, iterations=1)

train, test = data.load_data()
model.train(train, test)
model.save()
"""

model = als_model()
model.load()
print(model.score()['p@k']['train_mean'], model.score()['p@k']['test_mean'])


