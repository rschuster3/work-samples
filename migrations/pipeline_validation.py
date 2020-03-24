from rest_framework.exceptions import ValidationError

from apps.models.ndb import App
from maps.models.ndb import Map


def ed_2540_move_beacons(function_kwargs):
    """
    Serializer-level validation for ed_2540 migration. Check the correct arguments
    were supplied and that the maps and apps referred to actually exist. Infrom the
    user if an error occurs. This will preemptively stop the pipeline from running.
    """
    id_dict = function_kwargs.get("id_dict")
    ids = ["app_id_1", "map_id_1", "app_id_2", "map_id_2"]
    if not id_dict or any(i not in id_dict for i in ids) or not all(id_dict.get(i, None) for i in ids):
        raise ValidationError(
            'Please provide start and end Location IDs and start and end Floor IDs.'
            ' Example: {"id_dict": {"app_id_1": x, "map_id_1": x, "app_id_2": x, "map_id_2": x}}'
        )
    for i in ids:
        if i[:3] == "app" and not App.get_by_id(id_dict[i]):
            raise ValidationError(
                "Location with ID {} does not exist.".format(id_dict[i])
            )
        elif i[:3] == "map" and not Map.get_by_id(id_dict[i], namespace=str(id_dict['app' + i[3:]]) + '_1'):
            raise ValidationError(
                "Floor with ID {} does not exist.".format(id_dict[i])
            )
