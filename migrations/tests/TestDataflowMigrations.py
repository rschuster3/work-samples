from migrations import models
from migrations.dataflow_migrations.pipelines.test_migration import (
    non_namespaced_test_migration, namespaced_test_migration
)
from tests.TestCase import TestCase


class TestDataflowMigrations(TestCase):
    pass
    def test_namespaced_dataflow_migration(self):
        """
        Make sure we can call a pipeline without error. None, this doesn't
        check the pipeline actually ran on dataflow, it just means we can construct
        the pipeline using our base classes and not throw an error.
        """
        name = "Namespaced Test Migration"
        started_by = "test@test.com"
        function_kwargs = {}

        migration_history_obj = models.MigrationHistory(
            name=name,
            started_by=started_by,
            function_kwargs=function_kwargs,
        )
        migration_history_obj.put()

        namespaced_test_migration(
            **{
                "cloud": False,
                "name": "Namespaced Test Migration",
                "migration_history_obj": migration_history_obj
            }
        )
        assert True

    def test_non_namespaced_dataflow_migration(self):
        name = "Non Namespaced Test Migration"
        started_by = "test@test.com"
        function_kwargs = {}

        migration_history_obj = models.MigrationHistory(
            name=name,
            started_by=started_by,
            function_kwargs=function_kwargs,
        )
        migration_history_obj.put()

        non_namespaced_test_migration(
            **{
                "cloud": False,
                "migration_history_obj": migration_history_obj
            }
        )
        assert True
