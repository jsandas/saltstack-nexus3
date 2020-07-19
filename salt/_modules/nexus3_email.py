''''
execution module for Nexus 3 email settings

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
    'sls': 'highstate',
    'apply_': 'highstate',
    'highstate': 'highstate',
}

email_path = 'beta/email'


def configure(enabled,
            fromAddress='nexus@example.org',
            host='localhost',
            nexusTrustStoreEnabled=False,
            password=None,
            port=0,
            sslOnConnectEnabled=False,
            sslServerIdentityCheckEnabled=False,
            startTlsEnabled=False,
            startTlsRequired=False,
            subjectPrefix=None,
            username=''):
    '''
    enabled (bool):
        enable email support [True|False]

    fromAddress (str):
        mail from address (Default: nexus@example.org)

    host (string):
        smtp hostname (Default: localhost)

    nexusTrustStoreEnabled (bool):
        use nexus truststore [True|False] (Default: False)
        .. note::
            Ensure CA certificate is add to the Nexus trustore

    password (str):
        smtp password (Default: None)
       
    port (int):
        smtp port (Default: 0)

    sslOnConnectEnabled (bool):
        connect using tls (SMTPS) (Default: False)
        .. note::
            tls_connect and starttls should be mutually exclusive

    sslServerIdentityCheckEnabled (bool):
        verify server certificate (Default: False)

    startTlsEnabled (bool):
        enable starttls (Default: False)
        .. note::
            tls_connect and starttls should be mutually exclusive

    startTlsRequired (bool):
        require starttls (Default: False)
        .. note::
            tls_connect and starttls should be mutually exclusive

    subjectPrefix (str):
        prefix for subject in emails (Default: None)

    username (str):
        smtp username (Default: '')

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_email.configure enabled=True host=smtp.example.com

        salt myminion nexus3_email.configure enabled=False
    '''

    ret = {
        'email': {}
    }

    payload = {
        'enabled': enabled,
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'fromAddress': fromAddress,
        'subjectPrefix': subjectPrefix,
        'startTlsEnabled': startTlsEnabled,
        'startTlsRequired': startTlsRequired,
        'sslOnConnectEnabled': sslOnConnectEnabled,
        'sslServerIdentityCheckEnabled': sslServerIdentityCheckEnabled,
        'nexusTrustStoreEnabled': nexusTrustStoreEnabled
        }

    nc = nexus3.NexusClient()
    resp = nc.put(email_path, payload)

    if resp['status'] != 204:
        ret['comment'] = 'could not to configure emails settings.'
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }
        return ret
    
    email_config = describe()
    ret['email'] = email_config['email']

    return ret


def describe():
    '''
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_email.describe
    '''

    ret = {
        'email': {}
    }

    nc = nexus3.NexusClient()
    resp = nc.get(email_path)

    if resp['status'] == 200:
        ret['email'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'could not to retrieve email settings'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def reset():
    '''
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_email.reset
    '''

    ret = {}

    nc = nexus3.NexusClient()
    resp = nc.delete(email_path)

    if resp['status'] == 204:
        ret['comment'] = 'email settings reset'
    else:
        ret['comment'] = 'could not reset email settings'
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def verify(to):
    '''
    CLI Example:
    
    to (str):
        address to send test email to
    
    .. code-block:: bash

        salt myminion nexus3_email.verify
    '''
    ret = {}

    verify_path = email_path + '/verify'

    nc = nexus3.NexusClient()
    resp = nc.post_str(verify_path, to)

    if resp['status'] == 200:
        status = json.loads(resp['body'])
        if status['success']:
            ret['comment'] = 'email sent to {}.'.format(to)
        else:
            ret['comment'] = 'could not send email.'
            ret['error'] = status['reason']
    else:
        ret['comment'] = 'could not send email.'
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret   