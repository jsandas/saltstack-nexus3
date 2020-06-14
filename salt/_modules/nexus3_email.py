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

import nexus3

log = logging.getLogger(__name__)

__outputter__ = {
    "sls": "highstate",
    "apply_": "highstate",
    "highstate": "highstate",
}

email_path = 'beta/email'


def configure(enabled,
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
    enabled (bool):
        enable email support [True|False]

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

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_email.configure enabled=True host=smtp.example.com

        salt myminion nexus3_email.configure enabled=False
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

    nc = nexus3.NexusClient()
    resp = nc.put(email_path, payload)

    if resp['status'] != 204:
        ret['comment'] = 'Failed to retrieve emails settings.'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])
        return ret
    
    email_config = get()
    ret['email'] = email_config['email']

    return ret


def get():
    '''
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_email.get
    '''

    ret = {
        'email': {}
    }

    nc = nexus3.NexusClient()
    resp = nc.get(email_path)

    if resp['status'] == 200:
        ret['email'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'Failed to retrieve email settings'
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
        ret['comment'] = 'Email settings reset'
    else:
        ret['comment'] = 'Failed to reset email settings'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

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
            ret['comment'] = 'Success sending email to {}.'.format(to)
        else:
            ret['comment'] = 'Failed to send email.'
            ret['error'] = status['reason']
    else:
        ret['comment'] = 'Failed to send email.'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret   