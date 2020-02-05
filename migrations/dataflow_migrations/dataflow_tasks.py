import pickle
import logging

from apache_beam.io.gcp.datastore.v1.adaptive_throttler import AdaptiveThrottler
from apache_beam.io.gcp.datastore.v1 import helper as apache_helper
from celery import Celery, Task
from celery.utils.log import get_task_logger
from google.cloud.proto.datastore.v1.datastore_pb2 import Mutation

from .helpers import rpc_stats_callback
from .migration import migration, Status
from .pipelines.dataflow_settings import PROJECT


app = Celery('dataflow_tasks', backend='rpc://', broker='amqp://guest:guest@localhost:5672/')

# Set up logging to /var/log/celery/celery_tasks.log
logger = get_task_logger(__name__)
task_handler = logging.FileHandler('/var/log/celery/celery_tasks.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
task_handler.setFormatter(formatter)
logger.addHandler(task_handler)


class LogErrorsTask(Task):
    """
    Log task errors to celery logs to help us with debugging.

    Celery logs are at /var/log/celery/celery_err.log in the Docker
    container.
    """
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception('Celery task failure: %s' % exc, exc_info=exc)
        super(LogErrorsTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@app.task(base=LogErrorsTask)
def run_dataflow_migration(migration_history, **migration_kwargs):
    """
    Simply run the dataflow migration
    """
    logger.info('Running migration: ' + migration_kwargs.get('name'))

    try:
        migration_status = migration.call_registered(**migration_kwargs)
        monitor_migration_status(migration_status, pickle.loads(migration_history))
    except Exception as e:
        logger.exception(e)

    return


def monitor_migration_status(migration_status, migration_history_obj):
    """
    migration_history_obj must be pickled!

    Takes a pipeline status result and uses it to update MigrationHistory
    status as the migration runs.

    Calling forget() on this result will free up the worker to work on
    other tasks.
    """
    # Set up a datastore client
    project = PROJECT or 'meridianedit-staging'
    client = apache_helper.get_datastore(project)
    throttler = AdaptiveThrottler(window_ms=120000, bucket_ms=1000, overload_ratio=1.25)

    if migration_status == 'DONE':
        migration_history_obj.properties.get('status').string_value = Status.success
    elif migration_status in ['FAILED', 'CANCELLED', 'CANCELLING']:
        migration_history_obj.properties.get('status').string_value = Status.failed
    elif migration_status in ['STARTING', 'RUNNING', 'UPDATED', 'DRAINING', 'DRAINED']:
        migration_history_obj.properties.get('status').string_value = Status.running
    elif migration_status in ['PENDING', 'STOPPED'] :
        migration_history_obj.properties.get('status').string_value = Status.waiting
    elif migration_status == 'UNKNOWN':
        migration_history_obj.properties.get('status').string_value = Status.unknown
    else:
        # Sometimes migration status equals none of these things. Just assume success so
        # we can kick off post-migration work. This is based on observation in the wild.
        migration_history_obj.properties.get('status').string_value = Status.success

    # Write the mutated entity to the datastore
    mutations = [Mutation(update=migration_history_obj)]
    apache_helper.write_mutations(client, project, mutations, throttler, rpc_stats_callback)
