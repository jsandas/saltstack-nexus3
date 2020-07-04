''''
execution module for Nexus 3 security realms

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
    'sls': 'highstate',
    'apply_': 'highstate',
    'highstate': 'highstate',
}

realms_beta_path = 'beta/security/realms'


def list_active():
    '''
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_realms.list_active
    '''

    ret = {
        'realms': {},
    }

    path = realms_beta_path + '/active'
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp['status'] == 200:
        ret['realms'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'Failed to retrieve active realms.'
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def list_all():
    '''
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_realms.list_all
    '''

    ret = {
        'realms': {},
    }

    path = realms_beta_path + '/available'
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp['status'] == 200:
        ret['realms'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'Failed to retrieve available realms.'
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def reset():
    '''
    Resets realms to default

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_realms.reset
    '''

    ret = {
        'realms': {},
    }

    path = realms_beta_path + '/active'

    payload = [
        'NexusAuthenticatingRealm', 
        'NexusAuthorizingRealm'
    ]

    nc = nexus3.NexusClient()

    resp = nc.put(path, payload)

    if resp['status'] == 204:
        ret['realms'] = list_active()['realms']
        ret['comment'] = 'Realms reset to defaults.'
    else:
        ret['comment'] = 'Failed to reset realms.'
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def update(realms=[]):
    '''
    realms (list):
        list of realms in order they should be used 

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_realms.update realms="['NexusAuthenticatingRealm','NexusAuthorizingRealm','DockerToken']"
    '''

    ret = {
        'realms': {},
    }

    path = realms_beta_path + '/active'

    nc = nexus3.NexusClient()

    resp = nc.put(path, realms)

    if resp['status'] == 204:
        ret['realms'] = list_active()['realms']
        ret['comment'] = 'Realms updated.'
    else:
        ret['comment'] = 'Failed to update realms.'
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret