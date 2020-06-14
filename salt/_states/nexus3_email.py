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


def clear(name):
    '''
    name (str):
        state id name
        .. note::
            do not provide this argument, this is only here
            because salt passes this arg always

    .. code-block:: yaml

        clear_email:
          nexus3_email.clear

    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Email configuration will be reset to defaults'
        return ret

    reset_results = __salt__['nexus3_email.reset_email']()

    if 'error' in reset_results.keys():
        ret['result'] = False
        ret['comment'] = reset_results['error']
        return ret        

    ret['changes'] = reset_results

    return ret


def configure(name,
            enabled,
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
    name (str):
        state id name
        .. note::
            do not provide this argument, this is only here
            because salt passes this arg always

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

    .. code-block:: yaml

        setup_email:
          nexus3_email.configure:
            - enabled: True
            - host: smtp@example.com
            - port: 587
            - email_from: test@example.com
            - starttls_enabled: True
    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    # this is used only for the output when test=True
    email = {
        'enabled': enabled,
        'fromAddress': email_from,
        'host': host,
        'nexusTrustStoreEnabled': use_truststore,
        'password': password,
        'port': port,
        'sslOnConnectEnabled': tls_connect,
        'sslServerIdentityCheckEnabled': tls_verify,
        'startTlsEnabled': starttls_enabled,
        'startTlsRequired': starttls_required,
        'subjectPrefix': subject_prefix,
        'username': username
    }

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Email configuration will be change to {}.'.format(email)
        return ret

    configure_results = __salt__['nexus3_email.configure_email'](enabled,host,port,
                            use_truststore,username,password,email_from,subject_prefix,
                            starttls_enabled,starttls_required,tls_connect,tls_verify)

    log.warn(configure_results)
    if 'error' in configure_results.keys():
        ret['result'] = False
        ret['comment'] = configure_results['error']
        return ret        

    ret['changes'] = configure_results

    return ret