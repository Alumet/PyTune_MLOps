from model import als_model
import dotenv
import data

dotenv.load_dotenv()

model = als_model(factors=10, iterations=5)

train, test = data.load_data()
model.train(train, test)
model.save()

model = als_model()
model.load()
print(model.data_train.shape)

