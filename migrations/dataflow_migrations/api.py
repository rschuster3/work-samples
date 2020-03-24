import json
from datetime import datetime
import pickle

from flask import Flask, request, Response
from apache_beam.io.gcp.datastore.v1.adaptive_throttler import AdaptiveThrottler
from apache_beam.io.gcp.datastore.v1 import helper as apache_helper
from google.cloud.proto.datastore.v1 import entity_pb2
from google.cloud.proto.datastore.v1.datastore_pb2 import Mutation
from googledatastore import helper as datastore_helper

from .helpers import rpc_stats_callback
from .pipelines import migration
from .pipelines.dataflow_settings import PROJECT
from .dataflow_tasks import run_dataflow_migration


app = Flask(__name__)


def do_auth_stuff(endpoint):
### Some auth stuff I'd rather not share
    pass


def make_response(data, status_code=200):
    return Response(
        response=json.dumps(data),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/api/data-migrations', methods=['POST'])
@do_auth_stuff
def run_data_migration():
    request_data = json.loads(request.get_data())

    # Required fields
    fields = [
        'name',
        'function_kwargs',
        'user'
    ]

    # Some basic validation
    for f in fields:
        if f not in request_data:
            resp_data = json.dumps(
                {
                    'error': 'The ' + f + ' field is required.'
                }
            )
            resp = Response(resp_data, status=400, mimetype='application/json')
            return resp

    if request_data['name'] not in migration.choices:
        resp_data = json.dumps(
            {
                'error': 'The migration name is not valid.'
            }
        )
        resp = Response(resp_data, status=400, mimetype='application/json')
        return resp

    migration_name = request_data['name']
    function_kwargs = request_data['function_kwargs'] or {}
    user = request_data['user']

    function_kwargs.update({'name': migration_name})

    # Create a MigrationHistory entity to keep track of the migration status
    # set the project
    project = PROJECT or 'meridianedit-staging'

    # Create entity key
    partition_id = entity_pb2.PartitionId(project_id=project, namespace_id="")
    migration_history_obj_id = datetime.now().strftime("%Y%m%d%H%M%S")
    path_element = entity_pb2.Key.PathElement(kind="MigrationHistory", name=migration_history_obj_id)
    key = entity_pb2.Key(partition_id=partition_id, path=[path_element])

    # Create entity and give it properties
    entity = entity_pb2.Entity(key=key)
    property_dict = {
        'name': migration_name,
        'function_kwargs': json.dumps(function_kwargs),
        'started_by': user,
        'status': 'running',
        'created': datetime.now()
    }
    datastore_helper.add_properties(entity, property_dict)

    # Add entity to datastore
    mutations = [Mutation(insert=entity)]
    client = apache_helper.get_datastore(project)
    throttler = AdaptiveThrottler(window_ms=120000, bucket_ms=1000, overload_ratio=1.25)
    apache_helper.write_mutations(client, project, mutations, throttler, rpc_stats_callback)

    # Call the migration with any given function kwargs
    migration_kwargs = {
        'migration_history_obj': migration_history_obj_id,
    }
    migration_kwargs.update(function_kwargs)

    # Run the migration in a celery task worker to prevent it timing
    # out this connection. Also monitor the task so we can update
    # migration status.
    run_dataflow_migration.delay(pickle.dumps(entity), **migration_kwargs)

    resp_data = {
        'migration_history_obj_id': migration_history_obj_id
    }

    # A default 500 error message is returned if any of this breaks
    return Response(json.dumps(resp_data), status=200, mimetype='application/json')


@app.route('/_ah/data-migrations/health')
def health():
    return make_response('')


if __name__ == "__main__":
    app.run()
