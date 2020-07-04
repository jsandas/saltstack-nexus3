''''
execution module for Nexus 3 security privileges

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

privileges_beta_path = 'beta/security/privileges'


def create(name,
        privilege_type,
        actions=[],
        contentSelector=None,
        description='New Nexus privilege',
        domain=None,
        format=None,
        pattern=None,
        repository=None,
        scriptName=None):
    '''
    name (str):
        privilege name

    privilege_type (str):
        privilege type [application|repository-admin|respository-content-selector|repository-view|script|wildcard]

    actions (list):
        list of actions [ADD|ALL|BROWSE|CREATE|DELETE|EDIT|READ|UPDATE] (Default: [])

    contentSelector (str):
        name of content selector (Default: None
        .. note::
            content selector must exist before assigning privileges

    description (str):
        description of privilge (Default: 'New Nexus privilege')

    domain (str):
        domain of privilege [roles|scripts|search|selectors|settings|ssl-truststore|tasks|users|userschangepw] (Default: None)
        .. note::
            required for application privilege type

    format (str):
        respository format [bower|cocoapads|conan|docker|etc.] (Default: None)
        .. note::
            required for repository-admin, respository-content-selector, and repository-view privilege types

    pattern (regex):
        regex pattern to group other privileges (Default: None)
        .. note::
            required for wildcard privilege type

    repository (str):
        repository name (Default: None)
        .. note::
            required for repository-admin, respository-content-selector, and repository-view privilege types

    scriptName (str):
        script name (Default: None)

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_privileges.create name=nx-userschangepw actions="['ADD','READ']" description='Change password permission' domain=userschangepw privilege_type=application

        salt myminion nexus3_privileges.create name=nx-repository-view-nuget-nuget-hosted-browse actions=['BROWSE'] description='Browse privilege for nuget-hosted repository views' format=nuget repository=nuget-hosted privilege_type=repository-view
    '''

    ret = {
        'privilege': {}
    }

    path = privileges_beta_path + '/' + privilege_type

    payload = {
        'name': name,
        'description': description,
        'actions': actions,
    }

    application = {
        'domain': domain
    }

    repository = {
        'format': format,
        'repository': repository
    }

    repository_content_selector = {
        'format': format,
        'repository': repository,
        'contentSelector': contentSelector
    }

    script = {
        'scriptName': scriptName
    }

    wildcard = {
        'name': name,
        'description': description,
        'pattern': pattern
    }

    if privilege_type == 'application':
        if domain is None:
            ret['comment'] = 'domain cannot be None for privilege_type {}'.format(privilege_type)
            return ret
        payload.update(application)

    if privilege_type in ['repository-admin','repository-view']:
        if format is None or repository is None:
            ret['comment'] = 'format and repository cannot be None for privilege_type {}'.format(privilege_type)
            return ret
        payload.update(repository)

    if privilege_type == 'repository-content-selector':
        if format is None or repository is None or contentSelector is None:
            ret['comment'] = 'format, contentSelector, and repository cannot be None for privilege_type {}'.format(privilege_type)
            return ret
        payload.update(repository_content_selector)   

    if privilege_type == 'scripts':
        if script is None:
            ret['comment'] = 'scriptName cannot be None for privilege_type {}'.format(privilege_type)
            return ret
        payload.update(script)

    if privilege_type == 'wildcard':
        if pattern is None:
            ret['comment'] = 'pattern cannot be None for privilege_type {}'.format(privilege_type)
            return ret
        payload = wildcard

    nc = nexus3.NexusClient()

    resp = nc.post(path, payload)

    if resp['status'] == 201:
        ret['comment'] = 'Created privilege {}.'.format(name)
        ret['privilege'] = describe(name)['privilege']
    else:
        ret['comment'] = 'Failed to create privilege.'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret
    

def delete(name):
    '''
    name (str):
        privilege name

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_privileges.delete nx-analytics-all
    '''

    ret = {}

    path = privileges_beta_path + '/' + name

    nc = nexus3.NexusClient()

    resp = nc.delete(path)

    if resp['status'] == 204:
        ret['comment'] = 'Deleted privilege {}.'.format(name)
    else:
        ret['comment'] = 'Failed to delete privilege.'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def describe(name):
    '''
    name (str):
        privilege name

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_privileges.describe nx-analytics-all
    '''

    ret = {
        'privilege': {},
    }

    path = privileges_beta_path + '/' + name
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp['status'] == 200:
        ret['privilege'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'Failed to retrieve privilege {}.'.format(name)
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def list_all():
    '''
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_privileges.list_all
    '''

    ret = {
        'privileges': {},
    }

    path = privileges_beta_path
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp['status'] == 200:
        ret['privileges'] = json.loads(resp['body'])
    else:
        ret['comment'] = 'Failed to retrieve available privileges.'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def update(name,
        actions=None,
        contentSelector=None,
        description=None,
        domain=None,
        format=None,
        pattern=None,
        repository=None,
        scriptName=None):
    '''
    name (str):
        privilege name

    actions (list):
        list of actions [ADD|ALL|CREATE|DELETE|EDIT|READ|UPDATE] (Default: None)

    contentSelector (str):
        name of content selector (Default: None)
        .. note::
            content selector must exist before assigning privileges

    description (str):
        description of privilege (Default: None)

    domain (str):
        domain of privilege [roles|scripts|search|selectors|settings|ssl-truststore|tasks|users|userschangepw] (Default: None)
        .. note::
            required for application privilege type

    format (str):
        respository format [bower|cocoapads|conan|docker|etc.] (Default: None)
        .. note::
            required for repository-admin, respository-content-selector, and repository-view privilege types

    pattern (regex):
        regex pattern to group other privileges (Default: None)
        .. note::
            required for wildcard privilege type

    repository (str):
        repository name (Default: None)
        .. note::
            required for repository-admin, respository-content-selector, and repository-view privilege types

    scriptName (str):
        script name (Default: None)

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_privileges.update name=testing actions="['ADD','READ']" description='Change password permission' domain=userschangepw privilege_type=application
    '''

    ret = {
        'privilege': {}
    }

    priv_description = describe(name)

    if 'error' in priv_description.keys():
        ret['comment'] = 'Failed to update privilege.'
        ret['error'] = priv_description['error']
        return ret

    meta = priv_description['privilege']

    path = privileges_beta_path + '/' + meta['type'] + '/' + name

    if actions is not None:
        meta['actions'] = actions

    if contentSelector is not None and 'contentSelector' in meta.keys():
        meta['contentSelctor'] = contentSelector

    if description is not None:
        meta['description'] = description

    if domain is not None and 'domain' in meta.keys():
        meta['domain'] = domain

    if format is not None and 'format' in meta.keys():
        meta['format'] = format

    if repository is not None and 'repository' in meta.keys():
        meta['repository'] = repository

    if pattern is not None and 'pattern' in meta.keys():
        meta['pattern'] = pattern
    
    if scriptName is not None and 'scriptName' in meta.keys():
        meta['scriptName'] = scriptName

    nc = nexus3.NexusClient()

    resp = nc.put(path, meta)

    if resp['status'] == 204:
        ret['comment'] = 'Updated privilege {}.'.format(name)
        ret['privilege'] = describe(name)['privilege']
    else:
        ret['comment'] = 'Failed to update privilege.'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret