import os


MAX_CONCURRENT_JOBS = 25
NAMESPACES_PER_PIPELINE = 25
PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', 'some-default-staging-project')

BUCKET = 'dataflow-bucket'
if PROJECT == 'some-non-default-prod-project':
    BUCKET = 'dataflow-bucket-prod'

__JSON = {
    "nope": "newp"
}
__JSON_STAGING = {
    "nope": "newp"
}
