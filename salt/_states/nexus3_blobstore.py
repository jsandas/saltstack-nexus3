''''
stage module for Nexus 3 blobstore

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

log = logging.getLogger(__name__)


def absent(name):
    '''
    name (str):
        Name of blobstore

    .. code-block:: yaml

        myblobstore:
          nexus3_blobstore.absent


        delete_myblobstore:
          nexus3_blobstore.absent:
            - name: myblobstore
    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    # get metadata of blobstore if it exists
    meta = __salt__['nexus3_blobstore.describe'](name)
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

        delete_results = __salt__['nexus3_blobstore.delete'](name)
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
            S3 blobstores are currently untested.

    s3_access_key_id (str):
        AWS Access Key for S3 bucket (Default: '')
        .. note::
            S3 blobstores are currently untested.

    s3_secret_access_key (str):
        AWS Secret Access Key for S3 bucket (Default: '')
        .. note::
            S3 blobstores are currently untested.


    .. code-block:: yaml

        myblobstore:
          nexus3_blobstore.present:
            - store_type: file


        myblobstore:
          nexus3_blobstore.present:
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
    meta = __salt__['nexus3_blobstore.describe'](name)
    exists = True

    if not meta['blobstore']:
        exists = False

    # if test is true
    if __opts__['test']:
        ret['result'] = None
        
        if exists:
            if quota_type is None and meta['blobstore']['softQuota'] is not None:
                ret['comment'] = 'softQuota will be changed to None'
                return ret

            if quota_type is not None and meta['blobstore']['softQuota'] is not None:
                if quota_type != meta['blobstore']['softQuota']['type']:
                    meta['blobstore']['softQuota']['type'] = quota_type
                if quota_limit != meta['blobstore']['softQuota']['limit']:
                    meta['blobstore']['softQuota']['limit'] = quota_limit
                ret['comment'] = 'softQuota will be changed to: {}'.format(meta['blobstore']['softQuota'])
                return ret
        
            if quota_type is not None and meta['blobstore']['softQuota'] is None:
                meta['blobstore']['softQuota'] = {}
                meta['blobstore']['softQuota']['type'] = quota_type
                meta['blobstore']['softQuota']['limit'] = quota_limit
                ret['comment'] = 'softQuota will be changed to: {}'.format(meta['blobstore']['softQuota'])
                return ret

        ret['comment'] = 'blobstore {} will be created: store_type: {} quota_type: {} quota_limit: {}'.format(name, store_type, quota_type, quota_limit)

        if quota_type is None:
            ret['comment'] = 'blobstore {} will be created: store_type: {}'.format(name, store_type)  
      
        return ret
  
    if exists:
        if meta['blobstore']['softQuota'] is not None:
            update = False
            if quota_type != meta['blobstore']['softQuota']['type']:
                update = True
            if quota_limit != meta['blobstore']['softQuota']['limit']:
                update = True

            if update:
                update_results = __salt__['nexus3_blobstore.update'](name, quota_type, quota_limit)
                if 'error' in update_results.keys():
                    ret['result'] = False
                    ret['comment'] = update_results['error']
                    return ret

                ret['changes'] = update_results

        if meta['blobstore']['softQuota'] is None:
            update_results = __salt__['nexus3_blobstore.update'](name, quota_type, quota_limit)
            if 'error' in update_results.keys():
                ret['result'] = False
                ret['comment'] = update_results['error']
                return ret

            ret['changes'] = update_results    

        return ret        

    create_results = __salt__['nexus3_blobstore.create'](name, quota_type, quota_limit, store_type)
    if 'error' in create_results.keys():
        ret['result'] = False
        ret['comment'] = create_results['error']
        return ret

    ret['changes'] = create_results  

    return ret