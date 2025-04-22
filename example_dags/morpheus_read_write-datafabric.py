from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

default_args = {
    'start_date': days_ago(1),
}

with DAG(
    dag_id='morpheus_read_write-datafabric',    
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
) as dag:


    create_file = KubernetesPodOperator(
        task_id='create_file',
        name='create-file',
        namespace='airflow',
        image='bash:latest',
        cmds=['bash', '-c'],
        labels={"app": "airflow"},
        arguments=["echo 'Hello from Airflow morpheus volume!' > /mnt/datafabric-volume/morpheus-airflow.txt"],
        is_delete_operator_pod=True,
    )

    read_file = KubernetesPodOperator(
        task_id='read_file',
        name='read-file',
        namespace='airflow',
        image='bash:latest',
        cmds=['bash', '-c'],
        labels={"app": "airflow"},
        arguments=["cat /mnt/datafabric-volume/morpheus-airflow.txt"],
        is_delete_operator_pod=True,
    )

    create_file >> read_file

