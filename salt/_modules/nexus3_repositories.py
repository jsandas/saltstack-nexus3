''''
execution module for the Nexus 3 respositories

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

repo_beta_path = 'beta/repositories'
repo_v1_path = 'v1/repositories'


def delete(name):
    '''
    name (str):
        name of repository
    
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_repository.delete name=maven-central
    '''

    ret = {
        'comment': 'Repository {} deleted'.format(name)
    }

    delete_path = repo_beta_path + '/' + name

    nc = nexus3.NexusClient()
    resp = nc.delete(delete_path)

    if resp['status'] == 404:
        ret['comment'] = 'Repository {} not found.'.format(name)
    elif resp['status'] != 204:
        ret['comment'] = 'Error deleting repository {}.'.format(name)
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def describe(name):
    '''
    name (str):
        name of repository
    
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_repository.describe name=maven-central
    '''

    ret = {
        'repository': {}
    }

    nc = nexus3.NexusClient()
    resp = nc.get(repo_beta_path)

    if resp['status'] != 200:
        ret['comment'] = 'Error restrieving repository information for {}.'.format(name)
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])
        return ret

    repo_dict = json.loads(resp['body'])
    for repo in repo_dict:
        if repo['name'] == name:
            ret['repository'] = repo

    return ret


def list_all():
    '''
    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_repositories.list_all

    '''

    ret = {
        'repositories': {}
    }

    nc = nexus3.NexusClient()
    resp = nc.get(repo_v1_path)

    if resp['status'] != 200:
        ret['comment'] = 'Error retrieving repositories.'
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])
        return ret
    
    ret['repositories'] = resp['body']

    return ret


def create_proxy(name,
                repo_format,
                remote_url,
                blobstore='default',
                cleanup_policies=[],
                content_max_age=1440,
                apt_dist_name='bionic',
                apt_flat_repo=False,
                bower_rewrite_urls=True,
                docker_index_type='HUB',
                docker_index_url='',
                maven_version_policy='MIXED',
                maven_layout_policy='STRICT',
                nuget_cache_max_age=3600,
                metadata_max_age=1440,
                remote_password=None,
                remote_username=None,
                strict_content_validation=True,
                **kwargs):

    '''
    Nexus 3 supports many different formats.  The apt, bower, docker, maven, and nuget formats have built-in arguments.
    Parameters for other formats may be supplied as a dictionary as kwargs.  This would be useful for any new formats
    add to Nexus.

    name (str):
        Name of repository
    
    repo_format (str):
        Format of repository [apt|bower|cocoapads|conan|docker|etc.]
        .. note::
            This can be any officaly supported repository format for Nexus

    remote_url (str):
        Remote url to proxy

    blobstore (str):
        Name of blobstore to use (Default: default)
    
    cleanup_policies (list):
        List of cleanup policies to apply to repository (Default: [])

    content_max_age (int):
        Max age of content cache in seconds (Default: 1440)

    apt_dist_name (str):
        Apt distribution name (Default: bionic)

    apt_flat_repo (bool):
        Repo is flat ie: no folders (Default: False)

    bower_rewrite_urls (bool):
        Bower rewrite urls (Default: True)

    docker_index_type (str):
        Type of index for docker registry [REGISTRY|HUB|CUSTOM] (Default: HUB)
        .. note::
            If using CUSTOM then docker_index_url must be specified

    docker_index_url (str):
        Url for docker index
        .. note::
            If using CUSTOM then docker_index_url must be specified

    maven_version_policy (str):
        Type of marven artificats this repository stores [RELEASE|SNAPSHOT|MIXED] (default: MIXED)

    maven_layout_policy (str):
        Validate all paths are maven artifacts or metadata paths [STRICT|PERMISSIVE] (default: STRICT)

    nuget_cache_max_age (int):
        Nuget cache max age in seconds (Default: 3600)

    metadata_max_age (int):
        Max age of metadata cache in seconds (Default: 1440)

    remote_username (str):
        Username for remote url (Default: None)

    remote_password (str):
        Password for remote url (Default: None)

    strict_content_validation (bool):
        Enable strict content type validation [True|False] (Default: True)
    
    kwargs (dict):
        Any additional parameters for specific repository formats passed as a dictionary. 
        Check the Nexus 3 API docs for more information on other formats.
        .. example::
            apt='{'distribution': 'bionic', 'flat': False}'
        .. note::
            The above example is for reference.  Apt is fully supported with arguments in this function.
  }

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3.repositories.create_proxy name=test_raw repo_format=raw blobstore=raw_blobstore

        salt myminion nexus3_repositories.create_proxy name=test_apt repo_format=apt remote_url=http://test.example.com remote_username=bob remote_password=testing apt='{'distribution': 'bionic', 'flat':
 False}'
    '''

    ret = {
        'repository': {},
    }

    payload = {
        'name': name,
        'online': True,
        'storage': {
            'blobStoreName': blobstore,
            'strictContentTypeValidation': strict_content_validation
        },
        'cleanup': {
            'policyNames': cleanup_policies
        },
        'proxy': {
            'remoteUrl': remote_url,
            'contentMaxAge': content_max_age,
            'metadataMaxAge': metadata_max_age
        },
        'negativeCache': {
            'enabled': True,
            'timeToLive': 1440
        },
        'httpClient': {
            'blocked': False,
            'autoBlock': True,
            'connection': {
                'retries': 0,
                'userAgentSuffix': 'string',
                'timeout': 60,
                'enableCircularRedirects': False,
                'enableCookies': False
            }
        },
        'routingRule': 'string'
    }

    auth =  {
        'authentication': {
            'type': 'username',
            'username': remote_username,
            'password': remote_password
        }
    }

    apt = {
        'apt': {
            'distribution': apt_dist_name,
            'flat': apt_flat_repo
        }
    }

    bower = {
        'bower': {
            'rewritePackageUrls': bower_rewrite_urls
        }
    }

    docker = {
        'dockerProxy': {
            'indexType': docker_index_type,
            'indexUrl': docker_index_url
        }
    }

    maven = {
        'maven': {
            'versionPolicy': maven_version_policy,
            'layoutPolicy': maven_layout_policy
        }
    }

    nuget = {
        'nugetProxy': {
            'queryCacheItemMaxAge': nuget_cache_max_age
        }
    }

    if remote_username is not None:
        payload['httpClient'].update(auth)

    if repo_format == 'apt':
        payload.update(apt)

    if repo_format == 'bower':
        payload.update(bower)

    if repo_format == 'docker':
        payload.update(docker)
    
    if repo_format == 'maven':
        payload.update(maven)

    if repo_format == 'nuget':
        payload.update(nuget)

    if kwargs:
        payload.update(kwargs)

    metadata = describe(name)

    if metadata['repository']:
        ret['comment'] = 'Repository {} already exists.'.format(name)
        return ret

    create_path = repo_beta_path + '/' + repo_format + '/proxy'

    nc = nexus3.NexusClient()
    resp = nc.post(create_path, payload)

    if resp['status'] == 201:
        ret['repository'] = describe(name)['repository']
    else:
        ret['comment'] = 'Failed to create repository {}.'.format(name)
        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret