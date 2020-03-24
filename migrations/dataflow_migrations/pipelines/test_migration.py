from ..helpers import create_argv
from ..mappers import NamespacedDatastoreMigration, DatastoreMigration


def namespaced_test_migration(**kwargs):
    """
    Run migration that doesn't affect anything but behaves like normal
    migration based on namespaced dataflow migration.
    """
    model = "Campaign"

    # Run locally if cloud=False
    cloud = kwargs.get('cloud', True)
    argv = create_argv(kwargs.get('name')) if cloud else None  # Name added in flask app

    NamespacedDatastoreMigration(
        argv,
        kwargs.get('migration_history_obj'),
        model
    ).run()


def non_namespaced_test_migration(**kwargs):
    model = "App"

    # Run locally if cloud=False
    cloud = kwargs.get('cloud', True)
    argv = create_argv(kwargs.get('name')) if cloud else None  # Name added in flask app

    DatastoreMigration(
        argv,
        kwargs.get('migration_history_obj'),
        model
    ).run()
