''''
stage module for Nexus 3 users

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
        name of role

    .. code-block:: yaml

        testing1:
          nexus3_users.absent
    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    exists = True

    meta = __salt__['nexus3_users.describe'](name)
    
    if not meta['user']:
        exists = False

    if exists:
        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'user {} will be deleted.'.format(name)
            return ret

        resp = __salt__['nexus3_users.delete'](name)
        if 'error' in resp.keys():
            ret['result'] = False
            ret['comment'] = meta['error']
        else:
            ret['changes'] = resp
    else:
        ret['comment'] = 'user {} is not present'.format(name)

    return ret


# Dev Note: there may be a better way of handling create/update
# without requiring input for each argument
def present(name,
            password,
            emailAddress,
            firstName,
            lastName,
            roles=['nx-anonymous'],
            status='active'):
    '''
    name (str):
        name of user
    
    password (str):
        password of user

    emailAddress (str):
        email address
        .. note::
            password will always be updated as there is not
            a way to determine it's current value

    firstName (str):
        first name

    lastName (str):
        last name
    
    roles (list):
        list of roles (Default: ['nx-anonymous'])

    status (str):
        user status [active|disabled] (Default: active)

    .. code-block:: yaml

        create_user:
          nexus3_users.present:
            - name: test_role 
            - password: abc123
            - emailAddress: test@email.com
            - firstName: Test
            - lastName: User
            - roles: ['nx-admin']

        create_user:
          nexus3_users.present:
            - name: test_role 
            - password: abc123
            - emailAddress: test@email.com
            - firstName: Test
            - lastName: User
            - roles: ['nx-admin']
            - status: disabled

    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    exists = True
    # get value of realms
    meta = __salt__['nexus3_users.describe'](name)

    if meta['user'] == {}:
        exists = False

    if not exists:

        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'user {} will be created.'.format(name)
            return ret

        create_results = __salt__['nexus3_users.create'](name,password,emailAddress,firstName,lastName,roles,status)

        if 'error' in create_results.keys():
            ret['result'] = False
            ret['comment'] = create_results['error']
            return ret        

        ret['changes'] = create_results

    if exists:
        is_update = False
        updates = {}

        if meta['user']['emailAddress'] != emailAddress:
            meta['user']['emailAddress'] = emailAddress
            updates['emailAddress'] = emailAddress
            is_update = True

        if meta['user']['firstName'] != firstName:
            meta['user']['firstName'] = firstName
            updates['firstName'] = firstName
            is_update = True

        if meta['user']['lastName'] != lastName:
            meta['user']['lastName'] = lastName
            updates['lastName'] = lastName
            is_update = True

        if meta['user']['roles'] != roles:
            meta['user']['roles'] = roles
            updates['roles'] = roles
            is_update = True

        if meta['user']['status'] != status:
            meta['user']['status'] = status
            updates['status'] = status
            is_update = True

        if __opts__['test']:
            if is_update:
                ret['result'] = None
                ret['comment'] = 'user {} will be updated with: {}'.format(name, updates)
            else:
                ret['comment'] = 'user {} is in desired state.'.format(name)
            return ret

        # always update password because there isn't a way to 
        # determine if it is set to the provided value
        update_pw_results = __salt__['nexus3_users.update_password'](name,password)
        if is_update:
            update_results = __salt__['nexus3_users.update'](name,emailAddress,firstName,lastName,roles,status)

            if 'error' in update_results.keys() or 'error' in update_pw_results.keys():
                ret['result'] = False
                ret['comment'] = update_results['error'] or update_pw_results['error']
                return ret        

            ret['changes'] = updates
        else:
            ret['comment'] = 'user {} is in desired state.'.format(name)

    return ret
