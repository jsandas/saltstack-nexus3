''''
stage module for Nexus 3 blobstores

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

log = logging.getLogger(__name__)


def absent(name):
    '''
    name (str):
        Name of blobstore

    .. code-block:: yaml

        myblobstore:
          nexus3_blobstores.absent


        delete_myblobstore:
          nexus3_blobstores.absent:
            - name: myblobstore
    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    # get metadata of blobstore if it exists
    meta = __salt__['nexus3_blobstores.describe'](name)
    exists = True

    if not meta['blobstore']:
        exists = False

    if not exists:
        if __opts__['test']:
            ret['result'] = None
        
        ret['comment'] = 'blobstore {} not found'.format(name)

    # if test is true
    if exists:
        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'blobstore {} will be deleted'.format(name)
            return ret

        delete_results = __salt__['nexus3_blobstores.delete'](name)
        if 'error' in delete_results.keys():
            ret['result'] = False
            ret['comment'] = delete_results['error']
            return ret        

        ret['changes'] = delete_results

    return ret


def present(name,
        quota_type=None,
        quota_limit=1000000,
        store_type='file',
        s3_bucket='',
        s3_access_key_id='',
        s3_secret_access_key=''):
    '''
    name (str):
        Name of blobstore

    quota_type (str):
        Quota type [None|spaceRemainingQuota|spaceUsedQuota] (Default: None)

    quota_limit (int):
        Quota size in bytes (Default: 1000000)
        .. note::
            The limit should be no less than 1000000 bytes (1 MB) otherwise
            it does not display properly in the UI.

    store_type (str):
        Type of blobstore [file|s3] (Default: file)
        .. note::
            The blobstore name is used for blobstore path.

    s3_bucket (str):
        Name of S3 bucket (Default: '')
        .. note::
            S3 blobstores are currently not implemented.

    s3_access_key_id (str):
        AWS Access Key for S3 bucket (Default: '')
        .. note::
            S3 blobstores are currently not implemented.

    s3_secret_access_key (str):
        AWS Secret Access Key for S3 bucket (Default: '')
        .. note::
            S3 blobstores are currently not implemented.


    .. code-block:: yaml

        myblobstore:
          nexus3_blobstores.present:
            - store_type: file


        myblobstore:
          nexus3_blobstores.present:
            - store_type: file
            - quota_type: spaceUsedQuota
            - quota_limit: 5000000
    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    # get metadata of blobstore if it exists
    meta = __salt__['nexus3_blobstores.describe'](name)
    exists = True

    if not meta['blobstore']:
        exists = False

    if not exists:

        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'blobstore {} will be created.'.format(name)
            return ret


        create_results = __salt__['nexus3_blobstores.create'](name, quota_type, quota_limit, store_type)
        if 'error' in create_results.keys():
            ret['result'] = False
            ret['comment'] = create_results['error']
            return ret

        ret['changes'] = create_results  
  
    if exists:
        is_update = False
        updates = {}

        ret['comment'] = 'blobstore {} is in desired state'.format(name)

        if quota_type is None and meta['blobstore']['softQuota'] is not None:
            updates['quota_type'] = quota_type
            is_update = True

        if quota_type is not None and meta['blobstore']['softQuota'] is not None:
            if quota_type != meta['blobstore']['softQuota']['type']:
                updates['quota_type'] = quota_type
                is_update = True
            if quota_limit != meta['blobstore']['softQuota']['limit']:
                updates['quota_limit'] = quota_limit
                is_update = True

        if quota_type is not None and meta['blobstore']['softQuota'] is None:
            updates['quota_type'] = quota_type
            updates['quota_limit'] = quota_limit
            is_update = True

        if __opts__['test']:
            if is_update:
                ret['result'] = None
                ret['comment'] = 'blobstore {} will be updated with: {}'.format(name, updates)
            else:
                ret['comment'] = 'blobstore {} is in desired state.'.format(name)
            return ret

        if is_update:
            update_results = __salt__['nexus3_blobstores.update'](name, quota_type, quota_limit)
            if 'error' in update_results.keys():
                ret['result'] = False
                ret['comment'] = update_results['error']
                return ret

            ret['changes'] = updates
            ret['comment'] = ''

    return ret