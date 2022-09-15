from airflow.operators.bash import BashOperator
from datetime import timedelta, datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor
from airflow.utils.dates import days_ago
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'max_active_runs': 1,
    'retries': 3
}
dag = DAG(
    'spark_pi_sleep',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    tags=['example']
)
submit = SparkKubernetesOperator(
    task_id='spark_pi_submit',
    namespace='{{dag_run.conf.get("namespace", "sampletenant")}}',
    application_file="example_spark_kubernetes_operator_pi_with_dtap.yaml",
    kubernetes_conn_id="kubernetes_in_cluster",
    do_xcom_push=True,
    dag=dag,
    api_group="sparkoperator.hpe.com",
    enable_impersonation_from_ldap_user=False
)
sensor = SparkKubernetesSensor(
    task_id='spark_pi_monitor',
    namespace='{{dag_run.conf.get("namespace", "sampletenant")}}',
    application_name="{{ task_instance.xcom_pull(task_ids='spark_pi_submit')['metadata']['name'] }}",
    kubernetes_conn_id="kubernetes_in_cluster",
    dag=dag,
    api_group="sparkoperator.hpe.com",
    attach_log=True
)
ls_process = BashOperator(
    task_id='sleep_process',
    bash_command='ls /',
    dag=dag
)
submit >> sensor >> ls_process
