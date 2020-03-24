import multiprocessing

bind = ':8080'
workers = multiprocessing.cpu_count() * 2 + 1
threads = workers
keepalive = 10

# NO! This breaks datastore client and we don't need it
# worker_class = 'gevent'

# https://github.com/googleapis/google-cloud-python/issues/3486

# If we ever _did_ need it, we should add
# env_variables:
#  GOOGLE_CLOUD_DISABLE_GRPC: True
# to the app yaml.
