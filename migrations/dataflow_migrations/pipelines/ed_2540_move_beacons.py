import apache_beam as beam

from ..helpers import (
    create_argv, make_key, update_key_property, make_composite_filter, make_query
)
from ..mappers import DatastoreMigration


class MoveBeacons(DatastoreMigration):
    """
    Query all beacons with app=app_id_1 and map=map_id_1. Change their app to
    app_id_2 and their map to map_id_2. This will move the beacons from one
    map in one location to another map in another location.

    In other words, move beacons from app_1, map_1 to app_2, map_2.

    IDs come in an id_dict like so:

    id_dict = {
        "app_id_1": xxxx,
        "map_id_1": xxxx,
        "app_id_2": xxxx,
        "map_id_2": xxxx
    }

    """
    def __init__(self, argv, migration_history_obj, model, id_dict):
        # Extract IDs
        app_id_1 = id_dict.get("app_id_1")
        map_id_1 = id_dict.get("map_id_1")
        app_id_2 = id_dict.get("app_id_2")
        map_id_2 = id_dict.get("map_id_2")

        # Make these IDs into pb Keys
        self.app_key_1 = make_key('App', int(app_id_1), id_type='id', namespace='')
        self.map_key_1 = make_key('Map', int(map_id_1), id_type='id', namespace=str(app_id_1) + '_1')
        self.app_key_2 = make_key('App', int(app_id_2), id_type='id', namespace='')
        self.map_key_2 = make_key('Map', int(map_id_2), id_type='id', namespace=str(app_id_2) + '_1')

        super(MoveBeacons, self).__init__(argv, migration_history_obj, model)

    def query(self):
        # Set filters
        filter_dict = {
            'app': {
                'filter_type': 'EQUAL',
                'value': self.app_key_1
            },
            'map': {
                'filter_type': 'EQUAL',
                'value': self.map_key_1
            },
            'deleted': {
                'filter_type': 'EQUAL',
                'value': False
            }
        }
        filter_pb = make_composite_filter(filter_dict)

        # Create query
        query_pb = make_query(filter_pb, self.model)
        return query_pb

    def _create_pipeline(self, argv):
        p = beam.Pipeline(argv=argv)
        (
            p
            | self._get_source()
            | self.__class__.__name__ >> beam.Map(self._do_work, app_key_2=self.app_key_2, map_key_2=self.map_key_2)
            | self._get_sink()
        )
        return p

    @staticmethod
    def _do_work(entity, app_key_2=None, map_key_2=None):
        if not app_key_2 or not map_key_2:
            return entity

        # Update beacon.app and beacon.map
        update_key_property(entity, 'app', app_key_2)
        update_key_property(entity, 'map', map_key_2)

        return entity


def move_beacons(**kwargs):
    model = "Beacon2"

    return MoveBeacons(
        create_argv(kwargs.get("name")),
        kwargs.get("migration_history_obj"),
        model,
        kwargs.get("id_dict")
    ).run()
