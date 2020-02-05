from collections import OrderedDict, namedtuple


# Default migration status types
Status = namedtuple('Status', 'waiting,running,success,failed,unknown')(
    'waiting', 'running', 'success', 'failed', 'unknown'
)


# Default migration types
# search - Update search docs
# data - Farm out to migrations-flex service to run a Dataflow pipeline
# functional - Run some kind of function on file input or just in
#              general
MigrationTypes = namedtuple('MigrationTypes', 'search,data,functional')(
    'search', 'data', 'functional',
)


class Migration(object):
    """
    Declare Migration object inside the Flask app (migrations/migrations/) because
    otherwise it's not accessible to the Flask app when it's deployed. If it's 
    declared here, it'll be accessible to both the Flask app and the App Engine app.

    Instantiate the Migration object and import the dataflow pipeline migrations here
    so the names of all the migrations are available to api.py. Note the Migration object
    is also instanitated in migration/tasks/__init__.py
    """
    def __init__(self):
        self.func_map = OrderedDict()

    def register_as(self, path, name, migration_type):
        if migration_type not in MigrationTypes:
            raise Exception("Invalid migration type.")

        self.func_map[name] = {
            'path': path,
            'migration_type': migration_type,
        }

    def call_registered(self, name, **kwargs):
        if name == None:
            raise Exception("No migration name given.")

        func_dict = self.func_map.get(name, None)
        if func_dict is None:
            raise Exception("No functions registered against - " + str(name))

        if 'path' not in func_dict or not func_dict.get('path'):
            # Raise an error if this migration has no function listed to
            # run it from.
            raise Exception("No function listed for this migration.")

        # Fcn path is stored as a string to avoid having to import functions
        # that use dataflow in the __init__ script of migrations/tasks/
        path = func_dict['path']
        module_str = '.'.join(path.split('.')[:-1])
        func_str = path.split('.')[-1]
        module = __import__(module_str, fromlist=[''])
        func = getattr(module, func_str)
        kwargs.update({'name': name})
        try:
            result = func(**kwargs)
        except TypeError:
            result = func()

        return result

    @property
    def choices(self):
        return self.func_map.keys()

    def get_migration_type(self, name):
        return self.func_map.get(name, {}).get('migration_type', None)


migration = Migration()
