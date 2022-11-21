from model import als_model
import dotenv
import data


def train_model():
    model = als_model()
    train, test = data.load_data()
    model.train(train, test)
    score = model.score()
    print(score)
    db = data.DataBase.instance()
    db.save_score(score)
    model.save()


if __name__ == "__main__":
    dotenv.load_dotenv()
    train_model()
