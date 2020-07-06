''''
execution module for Nexus 3 blobstores

:configuration: In order to connect to Nexus 3, certain configuration is required
    in /etc/salt/minion on the relevant minions.

    Example:
      nexus3:
        host: '127.0.0.1:8081'
        user: 'admin'
        pass: 'admin123'

'''

import json
import logging

import nexus3

log = logging.getLogger(__name__)

__outputter__ = {
    "sls": "highstate",
    "apply_": "highstate",
    "highstate": "highstate",
}

blobstore_beta_path = 'beta/blobstores'
blobstore_v1_path = 'v1/blobstores'


def create(name,
        quota_type=None,
        quota_limit=1000000,
        store_type='file',
        s3_bucket='',
        s3_access_key_id='',
        s3_secret_access_key=''):
    '''
    name (str):
        Name of blobstore
        .. note::
            The blobstore name is used for blobstore path.  

    quota_type (str):
        Quota type [None|spaceRemainingQuota|spaceUsedQuota] (Default: None)

    quota_limit (int):
        Quota limit in bytes (Default: 1000000)
        .. note::
            The limit should be no less than 1000000 bytes (1 MB) otherwise
            it does not display properly in the UI.

    store_type (str):
        Type of blobstore file|s3] (Default: file)
        .. note::
            S3 blobstores are currently untested.

    s3_bucket (str):
        Name of S3 bucket (Default: '')
        .. note::
            S3 blobstores are currently untested.

    s3_access_key_id (str):
        AWS Access Key for S3 bucket (Default: '')
        .. note::
            S3 blobstores are currently untested.

    s3_secret_access_key (str):
        AWS Secret Access Key for S3 bucket (Default: '')
        .. note::
            The blobstore name is used for blobstore path.

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_blobstores.create name=myblobstore
        salt myminion nexus3_blobstores.create name=myblobstore quota_type=spaceRemainingQuota spaceRemainingQuota=5000000
    '''

    ret = {
        'blobstore': {},
    }

    path = '{}/{}'.format(blobstore_beta_path, store_type)

    payload = {
        'name': name,
        'path': '/nexus-data/blobs/' + name,
    }

    if quota_type is not None:
        payload['softQuota'] = {
            'type': quota_type,
            'size': quota_limit
        }

    nc = nexus3.NexusClient()

    resp = nc.get(path + '/' + name)

    if resp['status'] == 200:
        ret['comment'] = 'Blobstore "{}" already exists.'.format(name)
        return ret

    resp = nc.post(path, payload)

    if resp['status'] == 204:
        ret['blobstore'] = describe(name)['blobstore']
    else:
        ret['comment'] = 'Failed to create blobstore "{}".'.format(name)
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }


    return ret


def delete(name):
    '''
    name (str):
        Name of blobstore

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_blobstores.delete name=myblobstore
    '''

    ret = {
        'comment': 'Deleted blobstore "{}"'.format(name)
    }

    path = '{}/{}'.format(blobstore_beta_path, name)

    nc = nexus3.NexusClient()
    resp = nc.delete(path)

    if resp['status'] == 404:
        ret['comment'] = 'Blobstore "{}" does not exist.'.format(name)
    elif resp['status'] !=204 :
        ret['comment'] = 'Failed to delete blobstore "{}".'.format(name)
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def describe(name):
    '''
    name (str):
        Name of blobstore

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_blobstores.describe name=myblobstore
    '''

    ret = {
        'blobstore': {},
    }

    resp = list_all()

    if 'error' in resp.keys():
        ret['result'] = False
        ret['comment'] = 'Failed to retrieve blobstore "{}".'.format(name)
        ret['error'] = resp['error']
        return ret        

    for bstore in resp['blobstores']:
        if bstore['name'] == name:
            ret['blobstore'] = bstore
            break

    return ret


def list_all():
    '''
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_blobstores.list_all
    '''

    ret = {
        'blobstores': {}
    }

    nc = nexus3.NexusClient()
    resp = nc.get(blobstore_beta_path)

    if resp['status'] == 200:
        ret['blobstores'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'Failed to retrieve blobstores "{}".'
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def update(name,
        quota_type=None,
        quota_limit=1000000):
    '''
    .. note::
        Only blobstore quotas can be updated

    name (str):
        Name of blobstore
        .. note::
            The blobstore name is used for blobstore path.

    quota_type (str):
        Quota type [None|spaceRemainingQuota|spaceUsedQuota] (Default: None)

    quota_limit (int):
        Quota limit in bytes (Default: 1000000)
        .. note::
            The limit should be no less than 1000000 bytes (1 MB) otherwise
            it does not display properly in the UI.

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_blobstores.create name=myblobstore quota_type=spaceRemainingQuota quota_limit=5000000
    '''

    ret = {
        'blobstore': {}
    }

    payload = {
        'path': '/nexus-data/blobs/' + name,
    }

    if quota_type is not None:
        payload['softQuota'] = {
            'type': quota_type,
            'limit': quota_limit
        }

    metadata = describe(name)

    if not metadata['blobstore']:
        return metadata

    path = '{}/{}/{}'.format(blobstore_beta_path, metadata['blobstore']['type'].lower(), name)

    nc = nexus3.NexusClient()

    resp = nc.put(path, payload)

    if resp['status'] == 204:
        ret['blobstore'] = describe(name)['blobstore']
    else:
        ret['comment'] = 'Failed to update blobstore "{}".'.format(name)
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret
