"""Task group helpers methods"""
import logging

from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

from de_workshop.config import DBT_PROJECT_DIR

logger = logging.getLogger(__name__)


def dbt_task_group(model_name: str) -> TaskGroup:
    """
    Create a TaskGroup containing DBT run and test tasks for a model.

    Parameters
    ----------
    model_name : str
        The name of the DBT model.

    Returns
    -------
    TaskGroup
        The TaskGroup containing DBT tasks.
    """
    with TaskGroup(group_id=model_name) as tg:  # pylint: disable=C0103

        dbt_run = make_dbt_task(
            model=model_name,
            dbt_cmd="run",
        )
        logger.info(f"DBT Run: {dbt_run.task_id}")

        dbt_test = make_dbt_task(
            model=model_name,
            dbt_cmd="test",
        )
        logger.info(f"DBT Test: {dbt_test.task_id}")

        dbt_run >> dbt_test  # pylint: disable=W0104
    return tg


def make_dbt_task(
    model: str,
    dbt_cmd: str,
) -> BashOperator:
    """
    Create an Airflow operator for running or testing an individual DBT model.

    Parameters
    ----------
    model : str
        The name of the DBT model.
    dbt_cmd : str
        The DBT command to execute (e.g., "run", "test").

    Returns
    -------
    BashOperator
        The Airflow operator for the DBT task.
    """
    task_id = f"dbt_{dbt_cmd}_{model}"
    dbt_task = BashOperator(
        task_id=task_id,
        bash_command=get_dbt_cmd(dbt_cmd, model),
        trigger_rule=TriggerRule.ALL_DONE,
        retries=1,
    )
    return dbt_task


def get_dbt_cmd(dbt_cmd: str, model: str):
    """
    Generate the DBT command based on the provided arguments.

    Parameters
    ----------
    dbt_cmd : str
        The DBT command to generate (e.g., "run", "test").
    model : str
        The name of the DBT model.

    Returns
    -------
    str
        The generated DBT command.

    Raises
    ------
    ValueError
        If an invalid `dbt_cmd` is provided.
    """
    if dbt_cmd in ["debug"]:
        cmd = f"cd {DBT_PROJECT_DIR} && " f"poetry run dbt --no-write-json {dbt_cmd}"
    elif dbt_cmd in ["run", "test"]:
        cmd = (
            f"cd {DBT_PROJECT_DIR} && "
            f"poetry run dbt --no-write-json {dbt_cmd} --target {model} "
            f"--models {model} "
            f"--profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR} "
            "--vars 'execution_date: {{ ds }}'"
        )
    else:
        raise ValueError(f"`{dbt_cmd}` command not available")
    return cmd
