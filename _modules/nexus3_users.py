''''
execution module for Nexus 3 users

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

users_beta_path = 'beta/security/users'


def create(name,
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

    firstName (str):
        first name

    lastName (str):
        last name
    
    roles (list):
        list of roles (Default: ['nx-anonymous'])

    status (str):
        user status [active|disabled] (Default: active)

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_users.create name=test_user emailAddress="fake@email.com" password=testpassword firstName=Test lastName=User roles="['nx-admin']"
        
        .. note::
            running this command via the command-line could result in the password being saved
            is the user shell history
    '''

    ret = {
        'user': {},
    }

    path = users_beta_path

    payload = {
        'userId': name,
        'firstName': firstName,
        'lastName': lastName,
        'emailAddress': emailAddress,
        'password': password,
        'status': status,
        'roles': roles
    }

    nc = nexus3.NexusClient()

    resp = nc.post(path, payload)

    if resp['status'] == 200:
        ret['user'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'could not create user {}.'.format(name)
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def describe(name):
    '''
    name (str):
        name of user

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_users.describe test_user
    '''

    ret = {
        'user': {},
    }

    path = users_beta_path
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp['status'] == 200:
        users = json.loads(resp['body'])
        for user in users:
            if user['userId'] == name:
                ret['user'] = user
            
        return ret
    else:
        ret['comment'] = 'could not retrieve user {}.'.format(name)
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def delete(name):
    '''
    name (str):
        name of user

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_users.delete test_user
    '''
    ret = {}

    path = users_beta_path + '/' + name
    nc = nexus3.NexusClient()

    resp = nc.delete(path)

    if resp['status'] == 204:
        ret['comment'] = 'user {} deleted'.format(name)
    else:
        ret['comment'] = 'could not delete user {}.'.format(name)
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def list_all():
    '''
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_users.list_all
    '''

    ret = {
        'users': {},
    }

    path = users_beta_path
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp['status'] == 200:
        ret['users'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'could not retrieve users.'
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def update(name,
        emailAddress=None,
        firstName=None,
        lastName=None,
        roles=None,
        status=None):
    '''
    name (str):
        name of user

    emailAddress (str):
        email address (Default: None)

    firstName (str):
        first name (Default: None)

    lastName (str):
        last name (Default: None)
    
    roles (list):
        list of roles (Default: None)

    status (str):
        user status [active|disabled] (Default: None)

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_users.update name=test_user firstName=Testing roles="['nx-anonymous']"
    '''

    ret = {
        'user': {},
    }

    meta = describe(name)['user']

    if not meta:
        ret['comment'] = 'user {} does not exist'.format(name)
        return ret

    path = users_beta_path + '/' + name

    if emailAddress is not None:
        meta['emailAddress'] = emailAddress

    if firstName is not None:
        meta['firstName'] = firstName

    if emailAddress is not None:
        meta['lastName'] = lastName

    if roles is not None:
        meta['roles'] = roles

    if status is not None:
        meta['status'] = status

    nc = nexus3.NexusClient()

    resp = nc.put(path, meta)

    if resp['status'] == 204:
        ret['user'] = describe(name)['user']
    else:
        ret['comment'] = 'could not update user {}.'.format(name)
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret


def update_password(name,
                    password):
    '''
    name (str):
        name of user

    password (str):
        password

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_users.update_password name=test_user password=testing123

        .. note::
            running this command via the command-line could result in the password being saved
            is the user shell history
    '''

    ret = {
        'user': {},
    }

    meta = describe(name)['user']

    if not meta:
        ret['comment'] = 'user {} does not exist'.format(name)
        return ret

    path = users_beta_path + '/' + name + '/change-password'

    nc = nexus3.NexusClient()

    resp = nc.put_str(path, password)

    if resp['status'] == 204:
        ret['comment'] = 'updated password for {}.'.format(name)
    else:
        ret['comment'] = 'could not update password for {}.'.format(name)
        ret['error'] = {
            'code': resp['status'],
            'msg': resp['body']
        }

    return ret