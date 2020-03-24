from ..helpers import create_argv
from ..mappers import DatastoreMigration, NamespacedDatastoreMigration


class NamespacedUpdateModelSchema(NamespacedDatastoreMigration):
    """
    Given a list of one model class retrieve and put all its entities in the 
    datastore so the schema changes in the datastore.
    For example, if we add a calculated field to a model and want to populate
    it in all instances of that model, we'd run this migration.
    
    :param model: One model class name; required
        Example:
        ::
            {"model": "events.models.ndb.Event"}
    :param namespaced: Is this a namespaced model? Default is false
        Example:
        ::
            {"namespaced": true}

    :type model: class name as a string
    :type namespaced: boolean

    """
    @staticmethod
    def _do_work(entity):
        return entity


class NonNamespacedUpdateModelSchema(DatastoreMigration):
    """
    Given a list of one model class retrieve and put all the entities in the 
    datastore so the schema changes in the datastore. 
    For example, if we add a calculated field to a model and want to populate
    it in all instances of that model, we'd run this migration.
    
    :param model: One model class name; required
        Example:
        ::
            {"model": "apps.models.ndb.App"}
    :param namespaced: Is this a namespaced model? Default is false
        Example:
        ::
            {"namespaced": true}

    :type model: class name as a string
    :type namespaced: boolean

    """
    @staticmethod
    def _do_work(entity):
        return entity


def update_model_schema(**kwargs):
    """
    Given a type of model gets all of the instances from the datastore and puts them back in so the
    entity's field values update to reflect any new model schema. 

    A search index update task is run after this to reindex this model's search docs

    :param model: Required. A kwarg. Class name of model to perform migration on.
    :param namespaced: A kwarg. Default is False. Whether to do a namespaced migration or not.
    :param migration_history_obj: Provided by the serializer. A MigrationHistory entity that allows
        us to track the status of this migration

    :type model: string
    :type namespaced: boolean
    :type migration_history_obj: object

    """

    namespaced = kwargs.get("namespaced", False)  # Will default to non namespaced migration
    if namespaced:
        NamespacedUpdateModelSchema(
            create_argv(kwargs.get('name')),  # Name added in flask app
            kwargs.get('migration_history_obj', None),
            kwargs.get('model', None)
        ).run()
    else:
        NonNamespacedUpdateModelSchema(
            create_argv(kwargs.get('name')),  # Name added in flask app
            kwargs.get('migration_history_obj', None),
            kwargs.get('model', None)
        ).run()
