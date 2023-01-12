from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
import datetime
from utils.data import DataBase, load_data
from model.model import als_model
import os
import pandas as pd
from sqlalchemy import create_engine
import json
import requests

my_dag = DAG(
    dag_id='pytune',
    description='pytune model training',
    tags=['pytune'],
    schedule_interval='*/10 * * * *',
    catchup=False,
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(2),
    }
)


def test_DB_connection():
    os.environ["DATA_BASE"] = "mysql://root:pytune@DB/main"

    db = DataBase.instance()
    user = db.get_user_info('admin')

    if user.get('username') == ('admin'):
        return 0
    else:
        return 1


def score_old_model(task_instance):
    os.environ['MODEL_FOLDER'] = '/app/production/'
    os.environ['PRODUCTION_MODEL'] = '/app/production/model_als.mdl'

    model = als_model()
    model.load()

    score = model.score()

    task_instance.xcom_push(
        key="score_old",
        value=score
    )

    print(score)


def load_new_data():
    df = pd.read_csv('/app/data/dataset.csv', index_col=0)
    df_user_item = df[['user_id', 'track_id', 'time_stamp']]

    with open('/app/data/json_data.json', 'r') as file:
        info = json.load(file)

    today = str(datetime.datetime.now())
    last = info.get('last_load')

    df_user_item = df_user_item[(df_user_item['time_stamp'] < today) & (df_user_item['time_stamp'] > last)]

    with open('/app/data/json_data.json', 'w') as outfile:
        json.dump({'last_load': today}, outfile)

    values = [tuple(el) for el in df_user_item.values][::-1]

    connection_url = "mysql://root:pytune@DB/main"
    engine = create_engine(connection_url)

    with engine.connect() as connection:
        with connection.begin() as transaction:
            try:
                ins = f"INSERT INTO user_item VALUES (%s,%s,%s)"
                connection.execute(ins, values)
            except Exception as e:
                print(e)
                transaction.rollback()
            else:
                transaction.commit()

    print('done ok')
    print(df_user_item.count())


def train_new_model(task_instance):
    os.environ["DATA_BASE"] = "mysql://root:pytune@DB/main"
    model = als_model()
    train, test = load_data()
    model.train(train, test)
    score = model.score()
    model.save('/app/production/new_')

    task_instance.xcom_push(
        key="score_new",
        value=score
    )

    db = DataBase.instance()
    db.save_score(score)

    print(score)


def compare_model(task_instance):
    new = task_instance.xcom_pull(key=f"score_new")
    old = task_instance.xcom_pull(key=f"score_old")

    ndgc_new = round(new['50']['ndcg'], 3)
    ndgc_old = round(old['50']['ndcg'], 3)

    auc_new = round(new['50']['auc'], 3)
    auc_old = round(old['50']['auc'], 3)

    switch = False

    if auc_new >= auc_old - 0.01 and auc_new > 0.51:
        if ndgc_new >= ndgc_old - 0.01:
            switch = True

    task_instance.xcom_push(
        key="load_new_model",
        value=switch
    )


def change_model(task_instance):

    if task_instance.xcom_pull(key="load_new_model"):
        os.rename("/app/production/model_als.mdl", '/app/production/old_model_als.mdl')
        os.rename("/app/production/new_model_als.mdl", '/app/production/model_als.mdl')

        print("reload model")
    else:
        print("don't reload model")


def reload_model_api():
    x = requests.get('http://server:8000/admin/model/reload', auth=("admin", "admin"))
    assert x.status_code == 200


task_ping_test = PythonOperator(
    task_id='ping_test',
    python_callable=test_DB_connection,
    dag=my_dag
)

task_score_old = PythonOperator(
    task_id='score_old_model',
    python_callable=score_old_model,
    dag=my_dag
)

task_load_new = PythonOperator(
    task_id='load_new_data',
    python_callable=load_new_data,
    dag=my_dag
)

task_train_new = PythonOperator(
    task_id='train_model_on_new_data',
    python_callable=train_new_model,
    dag=my_dag
)

task_compare = PythonOperator(
    task_id='compare_new_to_old',
    python_callable=compare_model,
    dag=my_dag
)

task_change_model = PythonOperator(
    task_id='change_production_model',
    python_callable=change_model,
    dag=my_dag
)

task_load_model = PythonOperator(
    task_id='load_production_model',
    python_callable=reload_model_api,
    dag=my_dag
)

task_ping_test >> task_load_new
[task_load_new, task_score_old] >> task_train_new
task_train_new >> task_compare
task_compare >> task_change_model
task_change_model >> task_load_model