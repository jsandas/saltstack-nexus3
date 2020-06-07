''''
execution module for the Nexus 3 API

:configuration: In order to connect to Nexus 3, certain configuration is required
    in /etc/salt/minion on the relevant minions otherwise defaults are used. A sample dictionary might look
    like:
    
        nexus3:
          host: '127.0.0.1:8081'
          user: 'admin'
          pass: 'admin123'

'''

import json
import logging

import utils

# logging.basicConfig()
log = logging.getLogger(__name__)

# Define the module's virtual name and alias
__virtualname__ = "nexus3"

__outputter__ = {
    "sls": "highstate",
    "apply_": "highstate",
    "highstate": "highstate",
}


def __virtual__():
    '''
    Use virtualname
    '''
    return True


#### blobstore ####
blobstore_beta_path = 'beta/blobstores'
blobstore_v1_path = 'v1/blobstores'

def create_blobstore(name,
           quota_type=None,
           quota_limit=0,
           store_type='file',
           s3_bucket='',
           s3_access_key_id='',
           s3_secret_access_key=''):
    '''
    Create blobstore

    .. note::
        The blobstore name is used for blobstore path.  

    Args:
        name (str):
            Name of blobstore
        quota_type (str):
            Optional: Quota type
            Options: spaceRemainingQuota or spaceUsedQuota
            Default: None
        quota_limit (int):
            Optional: Quota size in bytes
            Default: 0
        store_type (str):
            Optional: Type of blobstore
            Options: file or s3
            Default: file
        s3_bucket (str):
            Optional: Name of S3 bucket
        s3_access_key_id (str):
            Optional: AWS Access Key for S3 bucket
        s3_secret_access_key (str):
            Optional: AWS Secret Access Key for S3 bucket

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3.create_blobstore name=myblobstore
        salt myminion nexus3.create_blobstore name=myblobstore quota_type=spaceRemainingQuota spaceRemainingQuota=5000000
    '''

    ret = {
        'comment': 'Created blobstore "{}"'.format(name)
    }

    path = '{}/{}'.format(blobstore_beta_path, store_type)

    payload = {
        'name': name,
        'path': name,
    }

    if quota_type is not None:
        payload['softQuota'] = {
            'type': quota_type,
            'size': quota_limit
        }

    nc = utils.NexusClient()

    exists = nc.get(path + '/' + name)

    if exists:
        ret['comment'] = 'Blobstore "{}" already exists.'.format(name)
        return ret

    resp = nc.post(path, payload)

    if not resp:
        ret['comment'] = 'Failed to create blobstore "{}".  See minion logs for details.'.format(name)

    return ret


def delete_blobstore(name):
    '''
    deletes specified blobstore

    Args:
        name (str):
            Name of blobstore

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3.delete_blobstore name=myblobstore
    '''

    ret = {
        'comment': 'Deleted blobstore "{}"'.format(name)
    }

    path = '{}/{}'.format(blobstore_beta_path, name)

    nc = utils.NexusClient()

    metadata = describe_blobstore(name)

    if not metadata['blobstore']:
        ret['comment'] = 'Blobstore "{}" does not exist.'.format(name)
        return ret

    resp = nc.delete(path)
    if not resp:
        ret['comment'] = 'Failed to delete blobstore "{}".  See minion logs for details.'.format(name)

    return ret


def describe_blobstore(name):
    '''
    returns metadata of specified blobstore

    Args:
        name (str):
            Name of blobstore

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3.describe_blobstore name=myblobstore
    '''

    ret = {
        'blobstore': {}
    }

    nc = utils.NexusClient()
    resp = nc.get(blobstore_beta_path)

    if not resp:
        ret['comment'] = 'Failed retrieving blobstore {}.  See minion logs for details.'.format(name)

    bstore_list = json.loads(resp.content)

    for bstore in bstore_list:
        if bstore['name'] == name:
            ret['blobstore'] = bstore
            break

    return ret


def list_blobstores():
    '''
    Lists all blobstores

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3.list_blobstores
    '''

    ret = {
        'blobstore': {}
    }

    nc = utils.NexusClient()
    resp = nc.get(blobstore_beta_path)

    if not resp:
        ret['comment'] = 'Faled retrieving blobstores.  See minion logs for details.'

    ret['blobstore'] = json.loads(resp.content)

    return ret


def update_blobstore(name,
           quota_type=None,
           quota_limit=0):
    '''
    Create blobstore

    .. note::
        The blobstore name is used for blobstore path.

    Args:
        name (str):
            Name of blobstore
        quota_type (str):
            Optional: Quota type
            Options: spaceRemainingQuota or spaceUsedQuota
            Default: None
        quota_limit (int):
            Optional: Quota size in bytes
            Default: 0

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3.create_blobstore name=myblobstore quota_type=spaceRemainingQuota quota_limit=5000000
    '''

    ret = {}

    payload = {
        'path': name,
        'softQuota': {
            'type': quota_type,
            'limit': quota_limit
        }
    }

    print(payload)
    metadata = describe_blobstore(name)

    if not metadata['blobstore']:
        ret['comment'] = 'Blobstore "{}" does not exist.'.format(name)
        return ret

    path = '{}/{}/{}'.format(blobstore_beta_path, metadata['blobstore']['type'].lower(), name)

    nc = utils.NexusClient()

    resp = nc.put(path, payload)

    if not resp:
        ret['comment'] = 'Failed to updating blobstore "{}".  See minion logs for details.'.format(name)

    ret = describe_blobstore(name)

    return ret

# print(update_blobstore("testing", "spaceRemainingQuota", 4000000))