import data


def train_model():
    train, test = data.load_data()
    print(train.shape)
    print(test.shape)

