''''
stage module for Nexus 3 security settings

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


def anonymous_access(name,
                    enabled):
    '''
    name (str):
        state id name
        .. note::
            do not provide this argument, this is only here
            because salt passes this arg always
    
    enabled (bool):
        enable or disable anonymous access [True|False]

    .. code-block:: yaml

        set_anonymous_access:
          nexus3_security.anonymous_access:
            - enabled: True
    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    is_update = False
    # get value of anonymous_access
    meta = __salt__['nexus3_anonymous_access.describe']()

    if 'error' in meta.keys():
        ret['result'] = False
        ret['comment'] = meta['error']
        return ret

    if meta['anonymous_access']['enabled'] != enabled:
        is_update = True

    if __opts__['test']:
        if is_update:
            ret['result'] = None
            ret['comment'] = 'anonymous_access will be set to {}.'.format(enabled)
        else:
            ret['comment'] = 'anonymous_access is in desired state: {}'.format(enabled)
        return ret

    if is_update:
        update_results = __salt__['nexus3_anonymous_access.enable'](enabled=enabled)

        if 'error' in update_results.keys():
            ret['result'] = False
            ret['comment'] = update_results['error']
            return ret        

        ret['changes'] = update_results
    else:
        ret['comment'] = 'anonymous_access is in desired state: {}'.format(enabled)

    return ret


def realms(name,
        realms):
    '''
    name (str):
        state id name
        .. note::
            do not provide this argument, this is only here
            because salt passes this arg always
    
    realms (list):
        list of realms in order they should be used 

    .. code-block:: yaml

        update_realms:
          nexus3_security.realms:
            - realms: ['NexusAuthenticatingRealm','NexusAuthorizingRealm','DockerToken']

        update_realms:
          nexus3_security.realms:
            - realms: 
              - NexusAuthenticatingRealm
              - NexusAuthorizingRealm
              - DockerToken
    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    is_update = False
    # get value of realms
    meta = __salt__['nexus3_realms.list_active']()

    if 'error' in meta.keys():
        ret['result'] = False
        ret['comment'] = meta['error']
        return ret

    if meta['realms'] != realms:
        is_update = True

    if __opts__['test']:
        if is_update:
            ret['result'] = None
            ret['comment'] = 'realms will be set to {}.'.format(realms)
        else:
            ret['comment'] = 'realms are in desired state'
        return ret

    if is_update:
        update_results = __salt__['nexus3_realms.update'](realms=realms)

        if 'error' in update_results.keys():
            ret['result'] = False
            ret['comment'] = update_results['error']
            return ret        

        ret['changes'] = update_results
    else:
        ret['comment'] = 'realms are in desired state'

    return ret
