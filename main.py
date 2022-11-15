from model import als_model
import dotenv
import data
from metric import auc_score

dotenv.load_dotenv()

"""model = als_model(factors=40, iterations=30)

train, test = data.load_data()
model.train(train, test)
model.save()"""


model = als_model()
model.load()

#model._auc()
print(model.score()['p@k']['train_mean'], model.score()['p@k']['test_mean'])

