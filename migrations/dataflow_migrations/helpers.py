import re
from oauth2client.service_account import ServiceAccountCredentials

from apache_beam.io.gcp.datastore.v1 import helper as apache_helper
from apache_beam.io.gcp.datastore.v1.adaptive_throttler import AdaptiveThrottler
from google.cloud.proto.datastore.v1 import query_pb2
from google.cloud.proto.datastore.v1.datastore_pb2 import Mutation, LookupRequest
from google.cloud.proto.datastore.v1.entity_pb2 import Key, PartitionId
from googledatastore import helper as datastore_helper
from googledatastore.connection import Datastore

from .pipelines.dataflow_settings import (
    BUCKET, PROJECT, __JSON, __JSON_EU, __JSON_STAGING
)


def clean_string_for_dataflow(string):
    # Make sure it's really a string
    string = str(string)

    # Convert string to lower case and replace space with dash
    string = string.lower().replace(' ', '-')

    # Remove all non alpha-numeric and non-dash characters
    string = re.sub("[^a-z0-9-]", "", string)

    return string


def create_argv(name):
    """
    Correctly format migration name so it can be used as a pipeline job name.

    Compile th arvg string for the pipeline job.
    """
    name = clean_string_for_dataflow(name)
    argv = [
        '--project={0}'.format(PROJECT),
        '--job_name=' + name,
        '--staging_location=gs://{0}/migrations/'.format(BUCKET),
        '--temp_location=gs://{0}/migrations/'.format(BUCKET),
        '--setup_file=./setup.py',
        '--runner=DataflowRunner'
    ]
    return argv


def rpc_stats_callback(successes=None, errors=None, failures=None, throttled_secs=None):
    pass


def make_key(kind, id, id_type='id', namespace=''):
    """
    Create a protobuf Key

    THIS DOES NOT SUPPORT ENTITIES WITH ANCESTORS. YOU'LL NEED TO MANUALLY
    CONSTRUCT YOUR OWN PATH ELEMENTS FOR KEYS WITH ANCESTORS.
    https://cloud.google.com/datastore/docs/reference/data/rpc/google.datastore.v1#key

    kind - string NDB kind (e.g. 'App', 'Campaign', 'Beacon2').
    id - string or int name or id (e.g. 5555555555555555 or 'some_entity_name')
    id_type - string id type. 'id' or 'name'. Defaults to 'id'.
    namespace - string namespace (e.g. '5555555555555555_1'). Defaults to ''.

    """
    partition_id = PartitionId(project_id=PROJECT, namespace_id=namespace)

    if id_type == 'id':
        path_element = Key.PathElement(kind=kind, id=int(id))
    else:
        path_element = Key.PathElement(kind=kind, name=str(id))

    return Key(partition_id=partition_id, path=[path_element])


def get_key_kind_and_id(key):
    """
    Given a Key protobuf object, return its kind and id or name.
    """
    path_element = key.path[-1]
    kind = path_element.kind

    if hasattr(path_element, 'name'):
        name_or_id = path_element.name
    else:
        name_or_id = path_element.id

    return kind, name_or_id


property_filter_dict = {
    'EQUAL': query_pb2.PropertyFilter.EQUAL,
    'LESS_THAN': query_pb2.PropertyFilter.LESS_THAN,
    'LESS_THAN_OR_EQUAL': query_pb2.PropertyFilter.LESS_THAN_OR_EQUAL,
    'GREATER_THAN': query_pb2.PropertyFilter.GREATER_THAN,
    'GREATER_THAN_OR_EQUAL': query_pb2.PropertyFilter.GREATER_THAN_OR_EQUAL,
    'HAS_ANCESTOR': query_pb2.PropertyFilter.HAS_ANCESTOR
}


def make_filter(field_name, value, filter_type='EQUAL'):
    """
    Filter for single key/value pair.

    field_name - String. Required. Name of field we want to filter on.
    value - Any type. Required. Value we want to change the field name to.
    filter_type - String. Default = 'EQUAL'. Type of filter we want.

    Other filter_types ("operators") are here:
    https://cloud.google.com/datastore/docs/reference/data/rpc/google.datastore.v1#google.datastore.v1.PropertyFilter.Operator
    """
    if not field_name or not value:
        raise Exception(
            'Please provide field name and value for this filter.'
        )

    if filter_type not in property_filter_dict:
        raise Exception(
            'Please provide a valid filter type.'
        )

    filter_pb = query_pb2.Filter()
    datastore_helper.set_property_filter(
        filter_pb,
        field_name,
        property_filter_dict[filter_type],
        value
    )
    return filter_pb


def make_composite_filter(filter_dict={}):
    """
    Filter for multiple key/value pairs

    filter_dict - {
            'some_field_name': {  # 'filter_type' and 'value' are required fields
                'filter_type': 'EQUAL',
                'value': 'bob'  # Can be any type of var
            }
        }
        filter_type must be 'EQUAL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'GREATER_THAN',
        'GREATER_THAN_OR_EQUAL', or 'HAS_ANCESTOR'
    """
    if not filter_dict:
        return None

    filter_pb = query_pb2.Filter()

    args = ()
    for k, v in filter_dict.iteritems():
        arg = datastore_helper.set_property_filter(
            query_pb2.Filter(),
            k,
            property_filter_dict.get(v.get('filter_type', 'EQUAL')),
            v.get('value', None)
        )
        args = args + (arg,)

    datastore_helper.set_composite_filter(
        filter_pb,
        query_pb2.CompositeFilter.AND,
        *args
    )

    return filter_pb


def make_query(filter_pb, kind):
    """
    Make a protobuf query object.

    filter_pb - a protobuf filter (output of make_composite_filter())
    kind - string NDB kind (e.g. 'App', 'Campaign', 'Beacon2').
    """
    query_pb = query_pb2.Query(filter=filter_pb)
    datastore_helper.set_kind(query_pb, kind)
    return query_pb


def set_entity_properties(entity, property_dict={}):
    """
    Set the value of one or more entity properties.

    entity - entity protobuf object
    property_dict - dict of key/value pairs of properties to update

    e.g. set_entity_properties(entity, {'foo': 'a', 'bar': [1, 2]})
    """
    datastore_helper.add_properties(entity, property_dict)


def get_entity_property(entity, property_name):
    """
    Get the value of an entity's property.

    entity - entity protobuf object
    property_name - String name of the entity property we want
        the value of
    """
    value_pb = entity.properties.get(property_name)
    if not value_pb:
        return None

    return datastore_helper.get_value(value_pb)


def update_key_property(entity, field_name, key):
    entity.properties.get(field_name).key_value.CopyFrom(key)


def fetch_entities(query_pb):
    """
    Run a given query to fetch entities.

    query_pb - A Query protobuf object; Required.

    Returns "an iterator of entities".
    """
    client = apache_helper.get_datastore(PROJECT)
    return apache_helper.fetch_entities(PROJECT, '', query_pb, client)


def make_mutation(mutation_type, entity=None, key=None):
    """
    Create a mutation, which is any change to an entity we want
    to push to the datastore. This can include updates, inserts,
    and deletes. This WILL directly change entities in the Datastore.
    Once a mutation is constructed, it must be added to a list and
    fed into apply_mutations() so that it is actually applied.

    mutation_type - String; Required; The type of mutation we're performing.
        Must be 'delete', 'update', 'insert', or 'upsert'.
    entity - Entity protobuf object. Required if migration_type is 'insert',
        'upsert', or 'update'.
    key - Key protobuf object. Required if migration_type is 'delete'.
    """
    if mutation_type not in ['delete', 'insert', 'upsert', 'update']:
        raise Exception(
            'Please provide a valid mutation type.'
        )

    if mutation_type == 'delete':
        if not key:
            raise Exception(
                'Please provide a Key protobuf object for this delete '
                'mutation.'
            )
        return Mutation(delete=key)

    elif mutation_type in ['insert', 'upsert', 'update']:
        if not entity:
            raise Exception(
                'Please provide an Entity protobuf object for this '
                'mutation.'
            )
        return Mutation(**{mutation_type: entity})


def apply_mutations(mutations):
    """
    Actually apply a list of muatations to the Datastore.

    mutations - list of Mutation protobuf objects. Required.
    """
    client = apache_helper.get_datastore(PROJECT)
    throttler = AdaptiveThrottler(window_ms=120000, bucket_ms=1000, overload_ratio=1.25)
    apache_helper.write_mutations(client, PROJECT, mutations, throttler, rpc_stats_callback)


def get_credentials():
    if PROJECT == 'some-non-default-prod-project':
        json = __JSON
    else:
        json = __JSON_STAGING

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        json,
        scopes=['https://www.googleapis.com/auth/datastore']
    )
    return credentials


def establish_connection():
    return Datastore(
        project_id=PROJECT,
        credentials=get_credentials()
    )


def lookup_by_key(key):
    """
    Given a Key protobuf object, use Datastore.LookupRequest to get the
    Entity (returned as an Entity protobuf object) corresponding to that Key.
    """
    # Get info from given key since this shitty lib requires us to rebuild
    # it instead of adding it directly to the request
    conn = establish_connection() 
    request = LookupRequest()
    request.keys.extend([key])
    response = conn.lookup(request)
    return response.found[0].entity
