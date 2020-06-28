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


def group(name,
        repo_format,
        blobstore='default',
        docker_force_auth=True,
        docker_http_port=None,
        docker_https_port=None,
        docker_v1_enabled=False,
        group_members=[],
        strict_content_validation=True,
        **kwargs):

    '''
    Nexus 3 supports many different formats.  The bower, docker, maven, and nuget formats have built-in arguments.
    Parameters for other formats may be supplied as a dictionary as kwargs.  This would be useful for any new formats
    add to Nexus.

    name (str):
        Name of repository
    
    repo_format (str):
        Format of repository [bower|cocoapads|conan|docker|etc.]
        .. note::
            This can be any officaly supported repository format for Nexus

    blobstore (str):
        Name of blobstore to use (Default: default)

    docker_force_auth (bool):
        Force basic authentication [True|False] (Default: True)

    docker_http_port (int):
        HTTP port for docker api (Default: None)
        .. note::
            Normally used if the server is behind a secure proxy

    docker_https_port (int):
        HTTPS port for docker api (Default: None)
        .. note::
            Normally used if the server is configured for https

    docker_v1_enabled (bool):
        Enable v1 api support [True|False] (Default: False)

    group_members (list):
        List of repositories in group (Default: [])
        .. note::
            The list cannot be empty.  An error will be returned

    strict_content_validation (bool):
        Enable strict content type validation [True|False] (Default: True)

    kwargs (dict):
        Any additional parameters for specific repository formats passed as a dictionary. 
        Check the Nexus 3 API docs for more information on other formats.
        .. example::
            yum='{'repodataDepth': 0, 'deployPolicy': 'STRICT'}
        .. note::
            The above example is for reference.  Yum repository groups do not have additional arguments.
  }

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_repositories.group name=test-yum-group repo_format=yum group_members=['test-yum']
    '''

    ret = {
        'repository': {},
    }

    payload = {
        'name': name,
        'online': True,
        'storage': {
            'blobStoreName': blobstore,
            'strictContentTypeValidation': strict_content_validation,
        },
        'group': {
            'memberNames': group_members
        }
    }

    docker = {
        'docker': {
            'v1Enabled': docker_v1_enabled,
            'forceBasicAuth': docker_force_auth,
        }
    }

    if repo_format == 'docker':
        if docker_http_port is not None:
            docker['docker']['httpPort'] = docker_http_port
        if docker_https_port is not None:
            docker['docker']['httpsPort'] = docker_https_port
        payload.update(docker)

    if kwargs:
        payload.update(kwargs)

    metadata = describe(name)

    update = False
    if metadata['repository']:
        update = True

    if not group_members:
        if update:
            ret['comment'] = 'Failed to update repository {}.'.format(name)
        else:
            ret['comment'] = 'Failed to create repository {}.'.format(name)

        ret['error'] = 'group_members cannot be empty'
        return ret

    nc = nexus3.NexusClient()

    if update:
        update_path = repo_beta_path + '/' + repo_format + '/group/' + name
        resp = nc.put(update_path, payload)
        ret['comment'] = 'Updated respository {}.'.format(name)
    else:
        create_path = repo_beta_path + '/' + repo_format + '/group'
        resp = nc.post(create_path, payload)
        ret['comment'] = 'Created respository {}.'.format(name)

    if resp['status'] == 201 or resp['status'] == 204:
        ret['repository'] = describe(name)['repository']
    else:
        if update:
            ret['comment'] = 'Failed to update repository {}.'.format(name)
        else:
            ret['comment'] = 'Failed to create repository {}.'.format(name)

        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def hosted(name,
        repo_format,
        apt_dist_name='bionic',
        apt_gpg_passphrase='',
        apt_gpg_priv_key='',
        blobstore='default',
        cleanup_policies=[],
        docker_force_auth=True,
        docker_http_port=None,
        docker_https_port=None,
        docker_v1_enabled=False,
        maven_layout_policy='STRICT',
        maven_version_policy='MIXED',
        strict_content_validation=True,
        yum_deploy_policy='STRICT',
        yum_repodata_depth=0,
        write_policy='allow_once',
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

    apt_dist_name (str):
        Apt distribution name (Default: bionic)

    apt_gpg_passphrase (str):
        GPG signing private key passphrase (Default: '')

    apt_gpg_priv_key (str):
        GPG signing private key (Default: '')
        .. note::
            This is require for hosted apt repositories

    blobstore (str):
        Name of blobstore to use (Default: default)

    cleanup_policies (list):
        List of cleanup policies to apply to repository (Default: [])

    docker_force_auth (bool):
        Force basic authentication [True|False] (Default: True)

    docker_http_port (int):
        HTTP port for docker api (Default: None)
        .. note::
            Normally used if the server is behind a secure proxy

    docker_https_port (int):
        HTTPS port for docker api (Default: None)
        .. note::
            Normally used if the server is configured for https

    docker_v1_enabled (bool):
        Enable v1 api support [True|False] (Default: False)

    maven_layout_policy (str):
        Validate all paths are maven artifacts or metadata paths [STRICT|PERMISSIVE] (default: STRICT)

    maven_version_policy (str):
        Type of marven artificats this repository stores [RELEASE|SNAPSHOT|MIXED] (default: MIXED)

    strict_content_validation (bool):
        Enable strict content type validation [True|False] (Default: True)

    yum_deploy_policy (str):
        Validate that all paths are RPMs or yum metadata [STRICT|PERMISSIVE] (Default: STRICT)

    yum_repodata_depth (int):
        Specifies the repository depth where repodata folder(s) are created (Default: 0)

    write_policy (str):
        Controls if deployments of and updates to artifacts are allowed [allow|allow_once|deny] (Default: allow_once)

    kwargs (dict):
        Any additional parameters for specific repository formats passed as a dictionary. 
        Check the Nexus 3 API docs for more information on other formats.
        .. example::
            yum='{'repodataDepth': 0, 'deployPolicy': 'STRICT'}
        .. note::
            The above example is for reference.  Yum is fully supported with arguments in this function.
  }

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3.repositories.create_hosted name=test-raw repo_format=raw blobstore=raw_blobstore

        salt myminion nexus3_repositories.create_hosted name=test-yum repo_format=yum yum_repodata_depth=3 yum_deploy_policy=permissive
    '''

    ret = {
        'repository': {},
    }

    payload = {
        'name': name,
        'online': True,
        'storage': {
            'blobStoreName': blobstore,
            'strictContentTypeValidation': strict_content_validation,
            'writePolicy': write_policy
        },
        'cleanup': {
            'policyNames': cleanup_policies
        }
    }

    apt = {
        'apt': {
            'distribution': apt_dist_name,
        },
        'aptSigning': {
            'keypair': apt_gpg_priv_key
        }
    }

    docker = {
        'docker': {
            'v1Enabled': docker_v1_enabled,
            'forceBasicAuth': docker_force_auth,
        }
    }

    maven = {
        'maven': {
            'versionPolicy': maven_version_policy.upper(),
            'layoutPolicy': maven_layout_policy.upper()
        }
    }

    yum = {
        'yum': {
            'repodataDepth': yum_repodata_depth,
            'deployPolicy': yum_deploy_policy.upper()
        }
    }

    if repo_format == 'apt':
        if apt_gpg_passphrase != '':
            apt['aptSigning']['passphrase'] = apt_gpg_passphrase
        payload.update(apt)

    if repo_format == 'docker':
        if docker_http_port is not None:
            docker['docker']['httpPort'] = docker_http_port
        if docker_https_port is not None:
            docker['docker']['httpsPort'] = docker_https_port
        payload.update(docker)
    
    if repo_format == 'maven':
        payload.update(maven)

    if repo_format == 'yum':
        payload.update(yum)

    if kwargs:
        payload.update(kwargs)

    metadata = describe(name)

    update = False
    if metadata['repository']:
        update = True

    nc = nexus3.NexusClient()

    if update:
        update_path = repo_beta_path + '/' + repo_format + '/hosted/' + name
        resp = nc.put(update_path, payload)
        ret['comment'] = 'Updated respository {}.'.format(name)
    else:
        create_path = repo_beta_path + '/' + repo_format + '/hosted'
        resp = nc.post(create_path, payload)
        ret['comment'] = 'Created respository {}.'.format(name)

    if resp['status'] == 201 or resp['status'] == 204:
        ret['repository'] = describe(name)['repository']
    else:
        if update:
            ret['comment'] = 'Failed to update repository {}.'.format(name)
        else:
            ret['comment'] = 'Failed to create repository {}.'.format(name)

        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


def proxy(name,
        repo_format,
        remote_url,
        apt_dist_name='bionic',
        apt_flat_repo=False,
        blobstore='default',
        bower_rewrite_urls=True,
        cleanup_policies=[],
        content_max_age=1440,
        docker_index_type='HUB',
        docker_index_url='',
        maven_layout_policy='STRICT',
        maven_version_policy='MIXED',
        metadata_max_age=1440,
        nuget_cache_max_age=3600,
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

    apt_dist_name (str):
        Apt distribution name (Default: bionic)

    apt_flat_repo (bool):
        Repo is flat ie: no folders (Default: False)

    blobstore (str):
        Name of blobstore to use (Default: default)

    bower_rewrite_urls (bool):
        Bower rewrite urls (Default: True)
    
    cleanup_policies (list):
        List of cleanup policies to apply to repository (Default: [])

    content_max_age (int):
        Max age of content cache in seconds (Default: 1440)

    docker_index_type (str):
        Type of index for docker registry [REGISTRY|HUB|CUSTOM] (Default: HUB)
        .. note::
            If using CUSTOM then docker_index_url must be specified

    docker_index_url (str):
        Url for docker index
        .. note::
            If using CUSTOM then docker_index_url must be specified

    maven_layout_policy (str):
        Validate all paths are maven artifacts or metadata paths [STRICT|PERMISSIVE] (default: STRICT)

    maven_version_policy (str):
        Type of marven artificats this repository stores [RELEASE|SNAPSHOT|MIXED] (default: MIXED)

    metadata_max_age (int):
        Max age of metadata cache in seconds (Default: 1440)

    nuget_cache_max_age (int):
        Nuget cache max age in seconds (Default: 3600)

    remote_password (str):
        Password for remote url (Default: None)

    remote_username (str):
        Username for remote url (Default: None)

    strict_content_validation (bool):
        Enable strict content type validation [True|False] (Default: True)

    kwargs (dict):
        Any additional parameters for specific repository formats passed as a dictionary. 
        Check the Nexus 3 API docs for more information on other formats.
        .. example::
            apt='{'distribution': 'bionic', 'flat': False}'
        .. note::
            The above example is for reference.  Apt is fully supported with arguments in this function.

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3.repositories.proxy name=test_raw repo_format=raw blobstore=raw_blobstore

        salt myminion nexus3_repositories.proxy name=test_apt repo_format=apt remote_url=http://test.example.com remote_username=bob remote_password=testing apt='{'distribution': 'bionic', 'flat':
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
            'indexType': docker_index_type.upper(),
            'indexUrl': docker_index_url
        }
    }

    maven = {
        'maven': {
            'versionPolicy': maven_version_policy.upper(),
            'layoutPolicy': maven_layout_policy.upper()
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

    update = False
    if metadata['repository']:
        update = True

    nc = nexus3.NexusClient()

    if update:
        update_path = repo_beta_path + '/' + repo_format + '/proxy/' + name
        resp = nc.put(update_path, payload)
        ret['comment'] = 'Updated respository {}.'.format(name)
    else:
        create_path = repo_beta_path + '/' + repo_format + '/proxy'
        resp = nc.post(create_path, payload)
        ret['comment'] = 'Created respository {}.'.format(name)

    if resp['status'] == 201 or resp['status'] == 204:
        ret['repository'] = describe(name)['repository']
    else:
        if update:
            ret['comment'] = 'Failed to update repository {}.'.format(name)
        else:
            ret['comment'] = 'Failed to create repository {}.'.format(name)

        ret['error'] = 'code:{} msg:{}'.format(resp['status'], resp['body'])

    return ret


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
        ret['comment'] = 'Repository {} not present.'.format(name)
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