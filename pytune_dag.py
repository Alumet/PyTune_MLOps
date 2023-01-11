from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
import datetime
from utils.data import DataBase, load_data
from model.model import als_model
import os
import pandas as pd
from sqlalchemy import create_engine

my_dag = DAG(
    dag_id='pytune',
    description='pytune model training',
    tags=['pytune'],
    schedule_interval=None,
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

    connection_url = "mysql://root:pytune@DB/main"
    engine = create_engine(connection_url)

    with engine.connect() as connection:
        result = connection.execute("Select time_stamp from user_item ORDER BY time_stamp DESC limit 1;")
        ans = result.fetchall()[0][0]

    today = str(datetime.datetime.now())
    last = str(ans)

    df_user_item = df_user_item[(df_user_item['time_stamp'] < today) & (df_user_item['time_stamp'] > last)].count()

    print('done ok')


def train_new_model(task_instance):
    os.environ["DATA_BASE"] = "mysql://root:pytune@DB/main"
    model = als_model()
    train, test = load_data()
    model.train(train, test)
    score = model.score()
    model.save('app/production/new_')

    task_instance.xcom_push(
        key="score_new",
        value=score
    )

    print(score)


def compare_model(task_instance):
    new = task_instance.xcom_pull(key=f"score_new")
    old = task_instance.xcom_pull(key=f"score_old")

    print("new: ", round(new['50']['ndcg'], 4))
    print("old: ", round(old['50']['ndcg'], 4))


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

task_ping_test >> task_load_new
[task_load_new, task_score_old] >> task_train_new
task_train_new >> task_compare
