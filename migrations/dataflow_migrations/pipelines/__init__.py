# migrations/migrations/api.py uses this
from ..migration import migration

migration.register_as(
    'dataflow_migrations.pipelines.ed_2540_move_beacons.move_beacons',
    'ED_2540 Move beacons to new map',
    'data'
)
