from model.model import als_model
import dotenv
from utils import data


def train_model():
    print('Starting')
    model = als_model()

    print('loading data')
    train, test = data.load_data()
    print('Training model')
    model.train(train, test)
    score = model.score()
    print('score')
    print(score)
    db = data.DataBase.instance()
    db.save_score(score)
    print('Saving model')
    model.save()


if __name__ == "__main__":
    dotenv.load_dotenv()
    train_model()
