from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

default_args = {
    'start_date': days_ago(1),
}

with DAG(
    dag_id='test_volume_mount_dag',
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
) as dag:

    volume = k8s.V1Volume(
        name='test-volume',
        empty_dir=k8s.V1EmptyDirVolumeSource(),
    )

    volume_mount = k8s.V1VolumeMount(
        mount_path='/mnt/test',
        name='test-volume',
        read_only=False,
    )

    create_file = KubernetesPodOperator(
        task_id='create_file',
        name='create-file',
        namespace='airflow',
        image='bash:latest',
        cmds=['bash', '-c'],
        arguments=["echo 'Hello from Airflow volume!' > /mnt/datafabric-volume/testfile.txt"],
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
        arguments=["cat /mnt/datafabric-volume/testfile.txt"],
        volumes=[volume],
        volume_mounts=[volume_mount],
        is_delete_operator_pod=True,
    )

    create_file >> read_file

