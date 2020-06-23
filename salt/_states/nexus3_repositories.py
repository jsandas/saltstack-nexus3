''''
stage module for Nexus 3 repositories

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


def present(name,
        repo_format,
        repo_type,
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
        yum_repodata_depth=0,
        **kwargs):
    '''
    name (str):
        state id name
        .. note::
            do not provide this argument, this is only here
            because salt passes this arg always

    repo_format (str):
        Format of repository [apt|bower|cocoapads|conan|docker|etc.]
        .. note::
            This can be any officaly supported repository format for Nexus

    repo_type (str):
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
            Normally used if the server is behind a secure proxy

    docker_https_port (int):
        HTTPS port for docker api (Default: None)
        .. note::
            Normally used if the server is configured for https

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

    kwargs (dict):
        Any additional parameters for specific repository formats passed as a dictionary. 
        Check the Nexus 3 API docs for more information on other formats.
        .. example::
            apt='{'distribution': 'bionic', 'flat': False}'
        .. note::
            The above example is for reference.  Apt is fully supported with arguments in this function.

    .. code-block:: yaml

        create_repository:
          nexus3_repositories.present:
            - name: test-yum
            - repo_type: proxy
            - blobstore: yum-blobstore
            - remote_url: https://yum.example.com

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

    reset_results = __salt__['nexus3_repositories.r']()

    if 'error' in reset_results.keys():
        ret['result'] = False
        ret['comment'] = reset_results['error']
        return ret        

    ret['changes'] = reset_results

    return ret
