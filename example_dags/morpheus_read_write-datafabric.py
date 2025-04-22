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

    volume = k8s.V1Volume(
        name='my-shared-volume',
        persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name='test-datafabric-airflow-shared-volume')
    )

    volume_mount = k8s.V1VolumeMount(
        mount_path='/mnt/datafabric-volume',  # Path inside the container
        name='my-shared-volume',
        read_only=False
    )

    list_files = KubernetesPodOperator(
        task_id='create_file',
        name='create-file',
        namespace='airflow',
        image='bash:latest',
        cmds=['bash', '-c'],
        labels={"app": "airflow"},
        arguments=["ls -ali /mnt"],
        volumes=[volume],
        volume_mounts=[volume_mount],
        is_delete_operator_pod=True,
    )

    create_file = KubernetesPodOperator(
        task_id='create_file',
        name='create-file',
        namespace='airflow',
        image='bash:latest',
        cmds=['bash', '-c'],
        labels={"app": "airflow"},
        arguments=["echo 'Hello from Airflow morpheus volume!' > /mnt/datafabric-volume/morpheus-airflow.txt"],
        volumes=[volume],
        volume_mounts=[volume_mount],
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
        volumes=[volume],
        volume_mounts=[volume_mount],
        is_delete_operator_pod=True,
    )

    list_files >> create_file >> read_file
    

