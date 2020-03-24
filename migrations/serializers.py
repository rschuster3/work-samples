import json
import time
import requests

import settings
from google.appengine.ext import ndb
from rest_framework import serializers

from . import models
from . import tasks
from . import pipeline_validation
from .post_migration import poll_migration
from util.deferred import deferred
from util.migrations import QUEUE_NAME
from util.rest.gae_mixins import ModelSerializer
from util.rest import fields


class MigrationSerializer(serializers.Serializer):
    id = fields.KeyField(
        source='key', entity_name=models.MigrationHistory, required=False,
        read_only=True
    )
    created = fields.DateTimeField(source='local_date_time', read_only=True)
    name = serializers.CharField(read_only=True)
    started_by = serializers.CharField(read_only=True)
    function_kwargs = fields.JsonField(required=False, default=None)
    status = serializers.CharField(read_only=True)
    migration = serializers.ChoiceField(
        choices=tasks.migration.choices, write_only=True
    )

    @property
    def user(self):
        user = self.context['request'].user
        return user.email or user.full_name or user.first or user.last or user.type

    def create(self, validated_data):
        """
        Since this user has permissions to create a migration, either pass them through
        to our migration flex instance (if this is a data migration) or send them to our
        migration mapper here (if this is a search index migration).
        """
        migration_type = tasks.migration.get_migration_type(
            validated_data['migration']
        )
        function_kwargs = validated_data['function_kwargs'] or {}

        # Search index migrations (send to our mapper here)
        if migration_type in ['search', 'functional']:
    
            obj = models.MigrationHistory(
                name=validated_data['migration'],
                started_by=self.user,
                function_kwargs=function_kwargs,
            )
            obj.put()
    
            migration_kwargs = {
                'migration_history_obj': obj,
            }
            migration_kwargs.update(function_kwargs)
    
            tasks.migration.call_registered(
                validated_data['migration'],
                **migration_kwargs
            )
    
            return obj

        # Data migrations (send to flex instance with Dataflow)
        elif migration_type == 'data':
            self.dataflow_pipeline_validation(function_kwargs, validated_data['migration'])

            url = settings.PROTOCOL + 'migrations-flex-dot-' + settings.APPSPOT_HOST + '/api/data-migrations'
            json_data = {
                'name': validated_data.get('migration'),
                'function_kwargs': function_kwargs,
                'user': self.user
            }

            # Send migration to migrations-flex service; Use exponential backoff
            # since the service needs to be re-awoken sometimes
            for i in [2, 4, 8, 16]:
                try:
                    resp = requests.post(url, json=json_data)
                except requests.exceptions.ConnectionError as e:
                    if i == 16:
                        raise requests.exceptions.ConnectionError(e)
                    else:
                        time.sleep(i)
                        continue
                else:
                    break

            # Pass through errors
            if resp.status_code > 399 and resp.status_code < 600:
                raise Exception('HTTP ' + str(resp.status_code) + ': ' + resp.text)

            migration_history_obj_id = resp.json()['migration_history_obj_id']

            # Kick off a task to poll the migration history obj for success and kick off
            # any post-migration work
            deferred(
                poll_migration,
                migration_history_obj_id,
                1,  # number of turtles
                _queue=QUEUE_NAME
            )

            # If all is well, return the migration history obj we created
            obj = ndb.Key('MigrationHistory', migration_history_obj_id).get()
            return obj

    def dataflow_pipeline_validation(self, function_kwargs, migration_name):
        """
        All validation having to do with Dataflow pipeline kwargs. We want the API user
        to see useful validation errors immediately, so we validate here instead of inside
        the flex service that kicks off Dataflow pipelines.
        """
        if migration_name == "ED_2540 Move beacons to new map":
            pipeline_validation.ed_2540_move_beacons(function_kwargs)
