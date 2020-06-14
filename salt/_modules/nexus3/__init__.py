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
email_path = 'beta/email'

def create_blobstore(name,
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
            
    .. code-block:: bash

        salt myminion nexus3.create_blobstore name=myblobstore
        salt myminion nexus3.create_blobstore name=myblobstore quota_type=spaceRemainingQuota spaceRemainingQuota=5000000
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

    nc = utils.NexusClient()

    resp = nc.get(path + '/' + name)

    if resp['status'] == 200:
        ret['comment'] = 'Blobstore "{}" already exists.'.format(name)
        return ret

    resp = nc.post(path, payload)

    if resp['status'] == 204:
        ret['blobstore'] = describe_blobstore(name)['blobstore']
    else:
        ret['comment'] = 'Failed to create blobstore "{}".'.format(name)
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])


    return ret


def delete_blobstore(name):
    '''
    name (str):
        Name of blobstore

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

    if resp['status'] != 204:
        ret['comment'] = 'Failed to delete blobstore "{}".'.format(name)
        ret['error'] = '{} : {}'.format(resp['status'], resp['body'])

    return ret


def describe_blobstore(name):
    '''
    name (str):
        Name of blobstore

    .. code-block:: bash

        salt myminion nexus3.describe_blobstore name=myblobstore
    '''

    ret = {
        'blobstore': {},
    }

    nc = utils.NexusClient()
    resp = nc.get(blobstore_beta_path)

    if resp['status'] == 200:
        bstore_list = json.loads(resp['body'])

        for bstore in bstore_list:
            if bstore['name'] == name:
                ret['blobstore'] = bstore
                break
    else:
        ret['comment'] = 'Failed to retrieve blobstore "{}".'.format(name)
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def list_blobstores():
    '''
    .. code-block:: bash

        salt myminion nexus3.list_blobstores
    '''

    ret = {
        'blobstore': {}
    }

    nc = utils.NexusClient()
    resp = nc.get(blobstore_beta_path)

    if resp['status'] == 200:
        ret['blobstore'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'Failed to retrieve blobstores "{}".'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def update_blobstore(name,
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

    .. code-block:: bash

        salt myminion nexus3.create_blobstore name=myblobstore quota_type=spaceRemainingQuota quota_limit=5000000
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

    metadata = describe_blobstore(name)

    if not metadata['blobstore']:
        return metadata

    path = '{}/{}/{}'.format(blobstore_beta_path, metadata['blobstore']['type'].lower(), name)

    nc = utils.NexusClient()

    resp = nc.put(path, payload)

    if resp['status'] == 204:
        ret['blobstore'] = describe_blobstore(name)['blobstore']
    else:
        ret['comment'] = 'Failed to update blobstore "{}".'.format(name)
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


#### email ####
def configure_email(enabled=False,
                    host='localhost',
                    port=25,
                    use_truststore=False,
                    username='',
                    password='',
                    email_from='nexus@example.org',
                    subject_prefix='',
                    starttls_enabled=False,
                    starttls_required=False,
                    tls_connect=False,
                    tls_verify=False):
    '''
    If no arguments are provided, the configuration will be
    reset to default

    enabled (bool):
        enable email support [True|False] (Default: False)

    host (string):
        smtp hostname (Default: localhost)

    port (int):
        smtp port (Default: 25)

    use_truststore (bool):
        use nexus truststore [True|False] (Default: False)
        .. note::
            Ensure CA certificate is add to the Nexus trustore

    username (str):
        smtp username (Default: '')

    password (str):
        smtp password (Default: '')

    email_from (str):
        mail from address (Default: nexus@example.org)

    subject_prefix (str):
        prefix for subject in emails (Default: '')

    starttls_enabled (bool):
        enable starttls (Default: False)
        .. note::
            tls_connect and starttls should be mutually exclusive

    starttls_required (bool):
        require starttls (Default: False)
        .. note::
            tls_connect and starttls should be mutually exclusive

    tls_connect (bool):
        connect using tls (SMTPS) (Default: False)
        .. note::
            tls_connect and starttls should be mutually exclusive

    tls_verify (bool):
        verify server certificate (Default: False)

    .. code-block:: bash

        salt myminion nexus3.configure_email enabled=True host=smtp.example.com

        salt myminion nexus3.configure_email
    '''

    ret = {
        'email': {}
    }

    payload = {
        "enabled": enabled,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "fromAddress": email_from,
        "subjectPrefix": subject_prefix,
        "startTlsEnabled": starttls_enabled,
        "startTlsRequired": starttls_required,
        "sslOnConnectEnabled": tls_connect,
        "sslServerIdentityCheckEnabled": tls_verify,
        "nexusTrustStoreEnabled": use_truststore
        }

    nc = utils.NexusClient()
    resp = nc.put(email_path, payload)

    if resp['status'] != 204:
        ret['comment'] = 'Failed to retrieve emails settings.'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])
        return ret
    
    email_config = describe_email()
    ret['email'] = email_config['email']

    return ret


def describe_email():
    '''
    .. code-block:: bash

        salt myminion nexus3.describe_email
    '''

    ret = {
        'email': {}
    }

    nc = utils.NexusClient()
    resp = nc.get(email_path)

    if resp['status'] == 200:
        ret['email'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'Failed to retrieve emails settings'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def verify_email(to):
    '''
    to (str):
        address to send test email to
    
    .. code-block:: bash

        salt myminion nexus3.verify_email
    '''
    ret = {}

    verify_path = email_path + '/verify'

    nc = utils.NexusClient()
    resp = nc.post_str(verify_path, to)

    if resp['status'] == 200:
        status = json.loads(resp['body'])
        if status['success']:
            ret['comment'] = 'Success sending email to {}.'.format(to)
        else:
            ret['comment'] = 'Failed to send email.'
            ret['error'] = status['reason']
    else:
        ret['comment'] = 'Failed to send email.'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret   