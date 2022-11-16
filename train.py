from model import als_model
import dotenv
import data


def train_model():
    model = als_model()
    df_track, (train, test) = data.load_data()
    model.train(train, test)
    model.track_list = df_track
    print(model.score())
    model.save()


if __name__ == "__main__":
    dotenv.load_dotenv()
    train_model()
