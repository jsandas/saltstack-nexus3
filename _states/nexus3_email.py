''''
stage module for Nexus 3 email settings

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
        ret['comment'] = 'email configuration will be reset to defaults'
        return ret

    reset_results = __salt__['nexus3_email.reset']()

    if 'error' in reset_results.keys():
        ret['result'] = False
        ret['comment'] = reset_results['error']
        return ret        

    ret['changes'] = reset_results

    return ret


def configure(name,
            enabled,
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
    name (str):
        state id name
        .. note::
            do not provide this argument, this is only here
            because salt passes this arg always

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
            sslOnConnectEnabled and startTlsEnabled/startTlsRequired should be mutually exclusive

    sslServerIdentityCheckEnabled (bool):
        verify server certificate (Default: False)

    startTlsEnabled (bool):
        enable starttls (Default: False)
        .. note::
            sslOnConnectEnabled and startTlsEnabled/startTlsRequired should be mutually exclusive

    startTlsRequired (bool):
        require starttls (Default: False)
        .. note::
            sslOnConnectEnabled and startTlsEnabled/startTlsRequired should be mutually exclusive


    subjectPrefix (str):
        prefix for subject in emails (Default: None)

    username (str):
        smtp username (Default: '')

    .. code-block:: yaml

        setup_email:
          nexus3_email.configure:
            - enabled: True
            - host: smtp@example.com
            - port: 587
            - fromAddress: test@example.com
            - startTlsEnabled: True
    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    ret['comment'] = 'email configuration is in desired state.'
    is_update = False
    meta = __salt__['nexus3_email.describe']()
    updates = {}

    if 'error' in meta.keys():
        ret['result'] = False
        ret['comment'] = meta['error']
        return ret

    input_vars = locals()
    for k, v in meta['email'].items():
        if v != input_vars[k]:
            is_update = True
            updates[k] = input_vars[k]

    if is_update:
        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'email configuration will be updated with: {}'.format(updates)
            return ret

        configure_results = __salt__['nexus3_email.configure'](enabled,fromAddress,host,
                        nexusTrustStoreEnabled,password,port,sslOnConnectEnabled,
                        sslServerIdentityCheckEnabled,startTlsEnabled,startTlsRequired,
                        subjectPrefix,username)

        if 'error' in configure_results.keys():
            ret['result'] = False
            ret['comment'] = configure_results['error']
            return ret        

        ret['changes'] = configure_results

    return ret
