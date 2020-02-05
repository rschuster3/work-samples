import logging

import apache_beam as beam
from apache_beam.io.gcp.datastore.v1 import helper as apache_helper
from apache_beam.io.gcp.datastore.v1 import datastoreio
from google.cloud.proto.datastore.v1 import query_pb2
from googledatastore import helper

from .pipelines.dataflow_settings import (
    PROJECT, NAMESPACES_PER_PIPELINE, MAX_CONCURRENT_JOBS
)


class _DatastoreMigrationBase(object):
    PROJECT = PROJECT

    def __init__(self, argv, migration_history_obj, model):
        self.migration_history_obj = migration_history_obj

        if not model:
            raise Exception('This operation requires a model class name.')
        self.model = model

    def query(self):
        # Instantiate a filter protobuf
        # You MUST instantiate the filter before the query, then instantiate
        # the query with the filter.
        filter_pb = query_pb2.Filter()

        # Get all non-deleted model instances
        helper.set_property_filter(
            filter_pb,
            'deleted',
            query_pb2.PropertyFilter.EQUAL,
            False
        )

        # Instantiate a query protobuf
        query_pb = query_pb2.Query(
            filter=filter_pb
        )
        helper.set_kind(query_pb, self.model)

        return query_pb

    def _get_source(self):
        return 'DatastoreRead' >> datastoreio.ReadFromDatastore(
            self.PROJECT,
            self.query(),
        )

    @staticmethod
    def _do_work(entity):
        return entity

    def _get_sink(self):
        return 'WriteToDatastore' >> datastoreio.WriteToDatastore(
            self.PROJECT
        )


class DatastoreMigration(_DatastoreMigrationBase):
    """
    Map a do-function over a non-namespaced (or single-namespaced) query

    The inheritor must implement the following:
     - a PROJECT class attribute
     - a do-function (do_work())
    """
    def __init__(self, argv, migration_history_obj, model):
        super(DatastoreMigration, self).__init__(argv, migration_history_obj, model)
        self._pipeline = self._create_pipeline(argv)

    def run(self):
        logging.info(
            "Dataflow job with MigrationHistory ID: " + str(self.migration_history_obj) + "."
        )
        return self._pipeline.run().wait_until_finish()

    def _create_pipeline(self, argv):
        p = beam.Pipeline(argv=argv)
        (
            p
            | self._get_source()
            | self.__class__.__name__ >> beam.Map(self._do_work)
            | self._get_sink()
        )
        return p


class NamespacedDatastoreMigration(_DatastoreMigrationBase):
    """
    Map a do-function over a query multiplexed across several namespaces.

    The inheritor must implement the following:
     - a PROJECT class attribute
     - a do-function (_do_work())
     - a method to get the namespaces across which to shard the query (
       get_namespaces())
    """
    _NAMESPACES_PER_PIPELINE = NAMESPACES_PER_PIPELINE

    def __init__(self, argv, migration_history_obj, model):
        super(NamespacedDatastoreMigration, self).__init__(argv, migration_history_obj, model)
        self.argv = argv
        self._namespaces = self.get_namespaces()

    def get_namespaces(self):
        # Skip auth-ing to db in test operations
        if not self.argv:
            return ['4952435991248896_1']

        query_pb = query_pb2.Query()
        helper.set_kind(query_pb, "__namespace__")
        client = apache_helper.get_datastore(PROJECT)
        namespace_entities = apache_helper.fetch_entities(PROJECT, '', query_pb, client)

        namespaces = []
        for n in namespace_entities:
            # Get namespace name or id
            key_path = n.key.path[-1]
            if key_path.HasField('id'):
                name_or_id = key_path.id
            else:
                name_or_id = key_path.name

            # Avoid duplicates and test namespaces
            if len(str(name_or_id)) > 1 and name_or_id not in namespaces:
                namespaces.append(name_or_id)

        return namespaces

    def run(self):
        """
        Each pipeline must be created and then run before the next pipeline is
        created. Otherwise the last job name to be assigned to argv will continue
        to be the job name and will conflict on dataflow.
        """
        logging.info(
            "Dataflow job with MigrationHistory ID: " + str(self.migration_history_obj) + "."
        )

        # Get NAMESPACES_PER_PIPELINE number of namespaces at a time. Also add on the last few namespaces.
        # So if NAMESPACES_PER_PIPELINE = 3 and self._namespaces is ['a', 'b', 'c', 'd], this gives:
        # [('a', 'b', 'c',), ('d',)]
        chunked_namespaces = zip(*[iter(self._namespaces)] * self._NAMESPACES_PER_PIPELINE)
        leftover_namespaces = self._namespaces[self._NAMESPACES_PER_PIPELINE * (len(self._namespaces) / self._NAMESPACES_PER_PIPELINE):]
        chunked_namespaces.append(tuple(leftover_namespaces))

        pause_trigger = 0
        for namespaces in chunked_namespaces:
            pipeline = self._create_pipeline(namespaces)

            # Return the status of the last pipeline
            if namespaces == chunked_namespaces[:-1]:
                return pipeline.run().wait_until_finish()

            # Wait until this batch of jobs finishes, then move on to the next
            # batch so we don't hit our concurrent jobs per project limit
            pause_trigger += 1
            if pause_trigger > MAX_CONCURRENT_JOBS - 5:
                pause_trigger = 0
                pipeline.run().wait_until_finish()
            else:
                pipeline.run()

    def _create_pipeline(self, namespaces):
        # Different pipelines have to have different job names
        # If original argv[1] = '--job_name=bob', and namespaces[0] is 'a', this gives:
        # argv[1] = '--job_name=bob-a'
        argv = self.argv[:]
        if argv:  # Don't do this during test
            original_job_name = argv[1].split('=')[1]
            job_name = original_job_name + '-' + str(namespaces[0]).lower().replace('_', '-').replace('.', '')
            argv[1] = argv[1].split('=')[0] + '=' + job_name

        p = beam.Pipeline(argv=argv)
        (
            (
                p | 'ReadNamespace_{}'.format(
                    ns
                ) >> datastoreio.ReadFromDatastore(
                    project=self.PROJECT,
                    query=self.query(),
                    namespace=ns
                )
                for ns in namespaces
            )
            | 'JoinNamespaceEntities' >> beam.Flatten()
            | self.__class__.__name__ >> beam.Map(self._do_work)
            | self._get_sink()
        )

        return p
