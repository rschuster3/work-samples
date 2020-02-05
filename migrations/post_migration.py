import time
import datetime

from google.appengine.ext import ndb

from migrations.dataflow_migrations.migration import Status
from migrations.models import MigrationHistory
from migrations.tasks.search_tasks import (
    restore_beacons_by_location, delete_stale_index_search_docs, reindex_by_model
)
from util.deferred import uuid_logger, deferred
from util.migrations import QUEUE_NAME


# How many times to spin off a new poll task to avoid the 10 minute time
# limit. This would be ~360 minutes' worth of tasks.
MAX_NUMBER_OF_TURTLES = 36


def ed_2540_move_beacons_post(migration_history_obj):
    """
    Run migrations to reindex beacon search docs at the new location and delete them
    at the old location.

    We've already verified app_id_1/2 is in the dict and the App exists.
    """
    # Delete stale search docs for the old location
    location_1 = migration_history_obj.function_kwargs.get('id_dict', {}).get('app_id_1')
    function_kwargs_1 = {
        'namespaces': [str(location_1) + '_1'],
        'index_names': ['omnibox'],
        'dry': False,
        'search_string': 'kind:beacon'
    }
    delete_stale_search_docs(migration_history_obj, function_kwargs_1)

    # Reindex beacon search docs at the new location
    location_2 = migration_history_obj.function_kwargs.get('id_dict', {}).get('app_id_2')
    function_kwargs_2 = {'location': location_2}
    new_migration_history_obj_2 = MigrationHistory(
        name='ED-2785 Restore beacon search docs by location(s)',
        started_by=migration_history_obj.started_by,
        function_kwargs=function_kwargs_2
    )
    new_migration_history_obj_2.put()

    function_kwargs_2.update(
        {
            'migration_history_obj': new_migration_history_obj_2
        }
    )
    restore_beacons_by_location(**function_kwargs_2)

    # Mark the apps as modified so our apps re-ping client_location_data
    # and the client_location_data cache is busted.
    # This is necessary for mobile apps to recognize beacons have moved.
    app_1 = ndb.Key('App', location_1).get()
    app_2 = ndb.Key('App', location_2).get()

    app_1.modified = datetime.datetime.now()
    app_2.modified = datetime.datetime.now()

    app_1.put()
    app_2.put()


@uuid_logger
def poll_migration(migration_history_obj_id, number_of_turtles):
    """
    Poll migration history object every minute to see if it has completed

    If the migration completes successfully, run its post migration work.

    If not, raise an error.

    If the migration is still running, keep spinning off new tasks to avoid the
    task queue time limit until we reach a point where this migration obviously
    isn't going to finish.
    """
    migration_history_obj = MigrationHistory.get_by_id(migration_history_obj_id)

    # We've tried long enough. The migration must be stuck in 'pending' or
    # otherwise broken.
    if number_of_turtles > MAX_NUMBER_OF_TURTLES:
        migration_history_obj.status = Status.failed
        migration_history_obj.put()

        raise Exception(
            'Migration {} failed and was unable to kick off'
            ' post migration work.'.format(migration_history_obj.name)
        )

    # Poll the migration for under 10 minutes (task execution time limit)
    start = datetime.datetime.now()
    while migration_history_obj.status not in [Status.success, Status.failed]:
        # Spin off another task to keep trying. We'll do this MAX_NUMBER_OF_TURTLES times
        if datetime.datetime.now() > start + datetime.timedelta(minutes=9):
            deferred(
                poll_migration,
                migration_history_obj_id,
                number_of_turtles + 1,
                _queue=QUEUE_NAME
            )
            return

        time.sleep(60)
        migration_history_obj = MigrationHistory.get_by_id(
            migration_history_obj_id,
            use_cache=False,
            use_memcache=False
        )

    # Spit out an error if the migration failed.
    if migration_history_obj.status == Status.failed:
        raise Exception(
            'Migration {} failed and was unable to kick off'
            ' post migration work.'.format(migration_history_obj.name)
        )

    # Run the correct post migration work function
    name = migration_history_obj.name
    if name == "ED_2540 Move beacons to new map":
        ed_2540_move_beacons_post(migration_history_obj)
