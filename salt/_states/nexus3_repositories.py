''''
stage module for Nexus 3 repositories

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
        name (str):
            name of respository

    .. code-block:: yaml

        delete_repository:
          nexus3_repositories.absent:
            - name: test-yum
    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    metadata = __salt__['nexus3_repositories.describe'](name=name)

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = ''

        if not metadata['repository']:            
            ret['comment'] = 'Repository {} not present.'.format(name)
        else:
            ret['comment'] = 'Repository {} will be deleted.'.format(name)
        return ret

    if not metadata['repository']:            
        ret['comment'] = 'Repository {} not present.'.format(name)
    else:
        resp = __salt__['nexus3_repositories.delete'](name)

        if 'error' in resp.keys():
            ret['result'] = False
            ret['comment'] = resp['error']
            return ret

        ret['changes'] = resp

    return ret


def present(name,
        format,
        type,
        apt_dist_name='bionic',
        apt_flat_repo=False,
        apt_gpg_passphrase='',
        apt_gpg_priv_key='',
        blobstore='default',
        bower_rewrite_urls=True,
        cleanup_policies=[],
        content_max_age=1440,
        docker_force_auth=True,
        docker_http_port=None,
        docker_https_port=None,
        docker_index_type='HUB',
        docker_index_url='',
        docker_v1_enabled=False,
        group_members=[],
        maven_layout_policy='STRICT',
        maven_version_policy='MIXED',
        metadata_max_age=1440,
        nuget_cache_max_age=3600,
        remote_password=None,
        remote_url='',
        remote_username=None,
        strict_content_validation=True,
        write_policy='allow_once',
        yum_deploy_policy='STRICT',
        yum_repodata_depth=0):
    '''
    name (str):
        name (str):
            name of respository

    format (str):
        Format of repository [apt|bower|cocoapads|conan|docker|maven2|etc.]
        .. note::
            This can be any officaly supported repository format for Nexus

    type (str):
        Repository type [hosted|group|proxy]

    apt_dist_name (str):
        Apt distribution name (Default: bionic)

    apt_flat_repo (bool):
        Repo is flat ie: no folders (Default: False)

    apt_gpg_passphrase (str):
        GPG signing private key passphrase (Default: '')

    apt_gpg_priv_key (str):
        GPG signing private key (Default: '')
        .. note::
            This is require for hosted apt repositories

    blobstore (str):
        Name of blobstore to use (Default: default)

    bower_rewrite_urls (bool):
        Bower rewrite urls (Default: True)
    
    cleanup_policies (list):
        List of cleanup policies to apply to repository (Default: [])

    content_max_age (int):
        Max age of content cache in seconds (Default: 1440)

    docker_force_auth (bool):
        Force basic authentication [True|False] (Default: True)

    docker_http_port (int):
        HTTP port for docker api (Default: None)
        .. note::
            Used if the server is behind a secure proxy

    docker_https_port (int):
        HTTPS port for docker api (Default: None)
        .. note::
            Used if the server is configured for https

    docker_index_type (str):
        Type of index for docker registry [REGISTRY|HUB|CUSTOM] (Default: HUB)
        .. note::
            If using CUSTOM then docker_index_url must be specified

    docker_index_url (str):
        Url for docker index
        .. note::
            If using CUSTOM then docker_index_url must be specified

    docker_v1_enabled (bool):
        Enable v1 api support [True|False] (Default: False)

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

    remote_url (str):
        Remote url to proxy

    remote_username (str):
        Username for remote url (Default: None)

    strict_content_validation (bool):
        Enable strict content type validation [True|False] (Default: True)

    write_policy (str):
        Controls if deployments of and updates to artifacts are allowed [allow|allow_once|deny] (Default: allow_once)

    yum_deploy_policy (str):
        Validate that all paths are RPMs or yum metadata [STRICT|PERMISSIVE] (Default: STRICT)

    yum_repodata_depth (int):
        Specifies the repository depth where repodata folder(s) are created (Default: 0)
    .. code-block:: yaml

        create_repository:
          nexus3_repositories.present:
            - name: test-yum
            - type: proxy
            - blobstore: yum-blobstore
            - remote_url: https://yum.example.com

    '''

    ret = {
        'name': name, 
        'changes': {}, 
        'result': True, 
        'comment': ''
    }

    exists = True
    meta = __salt__['nexus3_repositories.describe'](name=name)

    if 'error' in meta.keys():
        ret['result'] = False
        ret['comment'] = meta['error']
        return ret
    
    repo = meta['repository']
    is_update = False
    updates = {}

    if repo == {}:
        exists = False

    if exists:
        if type != repo['type'] or format != repo['format']:
            ret['result'] = False
            ret['comment'] = 'repository type and format cannot modified'
            return ret
        if blobstore != repo['storage']['blobStoreName']:
            updates['blobstore'] = blobstore
            is_update = True
        if strict_content_validation != repo['storage']['strictContentTypeValidation']:
            updates['strict_content_validation'] = strict_content_validation
            is_update = True

    if type == 'group':
        if exists:
            if group_members != repo['group']['memberNames']:
                updates['group_members'] = group_members
                is_update = True

            if format == 'docker':
                if docker_force_auth != repo['docker']['forceBasicAuth']:
                    updates['docker_force_auth'] = docker_force_auth
                    is_update = True
                if docker_v1_enabled != repo['docker']['v1Enabled']:
                    updates['docker_v1_enabled'] = docker_v1_enabled
                    is_update = True
                if docker_http_port != repo['docker']['httpPort']:
                    updates['docker_http_port'] = docker_http_port
                    is_update = True
                if docker_https_port != repo['docker']['httpsPort']:
                    updates['docker_https_port'] = docker_https_port
                    is_update = True

        if __opts__['test']:
            if exists:            
                if is_update:
                    ret['result'] = None
                    ret['comment'] = 'repository {} will be updated with: {}'.format(name, updates)
                else:
                    ret['comment'] = 'repository {} is in desired state'.format(name)
            else:
                ret['result'] = None
                ret['comment'] = 'repository {} will be created. Type: {} Format: {}'.format(name, type, format)
            return ret

        if exists and not is_update:      
            ret['comment'] = 'repository {} is in desired state'.format(name)
            return ret

        resp = __salt__['nexus3_repositories.group'](name,
                                                format,
                                                blobstore,
                                                docker_force_auth,
                                                docker_http_port,
                                                docker_https_port,
                                                docker_v1_enabled,
                                                group_members,
                                                strict_content_validation)

    if type == 'hosted':
        if exists:
            if repo['cleanup'] is not None and cleanup_policies != repo['cleanup']['policyNames']:
                updates['cleanup_policies'] = cleanup_policies
                is_update = True
            if write_policy != repo['storage']['writePolicy']:
                updates['write_policy'] = write_policy
                is_update = True

            if format == 'apt':
                if apt_dist_name != repo['apt']['distribution']:
                    updates['apt_dist_name'] = apt_dist_name
                    is_update = True
                # not sure if this is returned when describing a repo
                # if apt_gpg_passphrase != repo['aptSigning']['passphrase']:
                #     updates['apt_gpg_passphrase'] = apt_gpg_passphrase
                #     is_update = True
                if apt_gpg_priv_key != repo['aptSigning']['keypair']:
                    updates['apt_gpg_priv_key'] = apt_gpg_priv_key
                    is_update = True

            if format == 'docker':
                if docker_force_auth != repo['docker']['forceBasicAuth']:
                    updates['docker_force_auth'] = docker_force_auth
                    is_update = True
                if docker_v1_enabled != repo['docker']['v1Enabled']:
                    updates['docker_v1_enabled'] = docker_v1_enabled
                    is_update = True
                if docker_http_port != repo['docker']['httpPort']:
                    updates['docker_http_port'] = docker_http_port
                    is_update = True
                if docker_https_port != repo['docker']['httpsPort']:
                    updates['docker_https_port'] = docker_https_port
                    is_update = True

            if format == 'maven2':
                if maven_layout_policy != repo['maven']['layoutPolicy']:
                    updates['maven_layout_policy'] = maven_layout_policy
                    is_update = True
                if maven_version_policy != repo['maven']['versionPolicy']:
                    updates['maven_version_policy'] = maven_version_policy
                    is_update = True                

            if format == 'yum':
                if yum_deploy_policy != repo['yum']['deployPolicy']:
                    updates['yum_deploy_policy'] = yum_deploy_policy
                    is_update = True                          
                if yum_repodata_depth != repo['yum']['repodataDepth']:
                    updates['yum_repodata_depth'] = yum_repodata_depth
                    is_update = True

        if __opts__['test']:
            if exists:            
                if is_update:
                    ret['result'] = None
                    ret['comment'] = 'repository {} will be updated with: {}'.format(name, updates)
                else:
                    ret['comment'] = 'repository {} is in desired state'.format(name)
            else:
                ret['result'] = None
                ret['comment'] = 'repository {} will be created. Type: {} Format: {}'.format(name, type, format)
            return ret

        if exists and not is_update:      
            ret['comment'] = 'repository {} is in desired state'.format(name)
            return ret

        resp = __salt__['nexus3_repositories.hosted'](name,
                                                format,
                                                apt_dist_name,
                                                apt_gpg_passphrase,
                                                apt_gpg_priv_key,
                                                blobstore,
                                                cleanup_policies,
                                                docker_force_auth,
                                                docker_http_port,
                                                docker_https_port,
                                                docker_v1_enabled,
                                                maven_layout_policy,
                                                maven_version_policy,
                                                strict_content_validation,
                                                yum_deploy_policy,
                                                yum_repodata_depth,
                                                write_policy)

    if type == 'proxy':
        if exists:
            if remote_url != repo['proxy']['remoteUrl']:
                updates['remote_url'] = remote_url
                is_update = True
            if repo['cleanup'] is not None and cleanup_policies != repo['cleanup']['policyNames']:
                updates['cleanup_policies'] = cleanup_policies
                is_update = True
            if content_max_age != repo['proxy']['contentMaxAge']:
                updates['content_max_age'] = content_max_age
                is_update = True
            if metadata_max_age != repo['proxy']['metadataMaxAge']:
                updates['metadata_max_age'] = metadata_max_age
                is_update = True
            # cannot compare username as there is no way to determine if the same
            # if remote_password != repo['httpClient']['authentication']['password']:
            #     updates['remote_password'] = remote_password
            #     is_update = True
            if remote_username != repo['httpClient']['authentication']['username']:
                updates['remote_username'] = remote_username
                is_update = True

            if format == 'apt':
                if apt_dist_name != repo['apt']['distribution']:
                    updates['apt_dist_name'] = apt_dist_name
                    is_update = True
                if apt_flat_repo != repo['flat']:
                    updates['apt_flat_repo'] = apt_flat_repo
                    is_update = True

            if format == 'bower':
                if bower_rewrite_urls != repo['bower']['rewritePackageUrls']:
                    updates['bower_rewrite_urls'] = bower_rewrite_urls
                    is_update = True                

            if format == 'docker':
                if docker_index_type != repo['dockerProxy']['indexType']:
                    updates['docker_index_type'] = docker_index_type
                    is_update = True
                if docker_index_url != repo['dockerProxy']['indexUrl']:
                    updates['docker_index_url'] = docker_index_url
                    is_update = True

            if format == 'maven2':
                if maven_layout_policy != repo['maven']['layoutPolicy']:
                    updates['maven_layout_policy'] = maven_layout_policy
                    is_update = True
                if maven_version_policy != repo['maven']['versionPolicy']:
                    updates['maven_version_policy'] = maven_version_policy
                    is_update = True   

            if format == 'nuget':
                if nuget_cache_max_age != repo['nugetProxy']['queryCacheItemMaxAge']:
                    updates['nuget_cache_max_age'] = nuget_cache_max_age
                    is_update = True

        if __opts__['test']:
            if exists:            
                if is_update:
                    ret['result'] = None
                    ret['comment'] = 'repository {} will be updated with: {}'.format(name, updates)
                else:
                    ret['comment'] = 'repository {} is in desired state'.format(name)
            else:
                ret['result'] = None
                ret['comment'] = 'repository {} will be created. Type: {} Format: {}'.format(name, type, format)
            return ret

        if exists and not is_update:      
            ret['comment'] = 'repository {} is in desired state'.format(name)
            return ret

        resp = __salt__['nexus3_repositories.proxy'](name,
                                                    format,
                                                    remote_url,
                                                    apt_dist_name,
                                                    apt_flat_repo,
                                                    blobstore,
                                                    bower_rewrite_urls,
                                                    cleanup_policies,
                                                    content_max_age,
                                                    docker_index_type,
                                                    docker_index_url,
                                                    maven_layout_policy,
                                                    maven_version_policy,
                                                    metadata_max_age,
                                                    nuget_cache_max_age,
                                                    remote_password,
                                                    remote_username,
                                                    strict_content_validation)

    if 'error' in resp.keys():
        ret['result'] = False
        ret['comment'] = resp['error']
        return ret
     
    ret['changes'] = resp['repository']

    return ret
