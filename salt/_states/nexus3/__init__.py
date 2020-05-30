# -*- coding: utf-8 -*-
""""
State module for working with the Nexus 3 API

Based on the work in ThoTeam's project for ansible (https://github.com/ansible-ThoTeam/nexus3-oss).
The groovy scripts used by this state are copied from or based on the scripts
provided in this repository in the nexus_groovy.py file so they sync with the
module itself.

:depends: requests

:configuration: In order to connect to Nexus 3, certain configuration is required
    in /etc/salt/minion on the relevant minions otherwise defaults are used. A sample dictionary might look
    like:
    
        nexus3:
          host: '127.0.0.1:8081'
          user: 'admin'
          pass: 'admin123'

Enable or disable anonymous access to Nexus

.. code-block:: yaml

    allow_anonymous_access:
      nexus3.allow_anonymous_access:
        - option: False

Set base url for Nexus

.. code-block:: yaml

    http://localhost:8081:
      nexus3.base_url

Create blobstore

.. code-block:: yaml

    raw:
      nexus3.blobstore:
        - path: /nexus-data/blobs/raw

    # S3 hasn't been tested and does have
    # more options than just the three listed here

    s3-blobstore:
      nexus3.blobstore:
        - type: S3
        - s3_bucket: bucket-name
        - s3_access_key_id: access-key
        - s3_secret_access_key: secret-access-key

Enable Docker Bearer Token Realm

.. code-block:: yaml

    enable_docker_realm:
      nexus3.realms:
        - name: DockerToken
        - status: True

Create repo hosted for maven

.. code-block:: yaml
    maven-hosted:
      nexus3.repo_hosted:
        - repo_type: maven
        - blob_store: default
        - maven_version_policy: release
        - maven_layout_policy: strict
        - strict_content_validation: True

Create repo group for maven

.. code-block:: yaml
    maven-group:
      nexus3.repo_group:
        - repo_type: maven
        - member_repo:
          - maven-central
          - maven-local
        - strict_content_validation: True

Create repo proxy for yum
Note: the blob_store in this example needs to be created first

.. code-block:: yaml
    yum-proxy:
      nexus3.repo_proxy:
        - type: yum
        - remote_url: 'http://mirrors.centos.org/7/x86_64'
        - blob_store: yum
        - strict_content_validation: True

Create role

.. code-block:: yaml

    repo-user:
      nexus3.role:
        - description: 'Read only user'
        - privileges:
          - nx-repository-view-*-*-read
        - roles:
          - repo-user

Create task for database backup
Note: The key/values under task_properties is indented 4 spaces instead
of two.  This is how salt creates a dictionary from the yaml

.. code-block:: yaml

    database_backup:
      nexus3.tasks:
        - task_type_id: 'db.backup'
        - task_properties:
            location:'/nexus-data/backup'
        - task_cron: '0 0 21 * * ?'

Create user
Note: role(s) must exist first

.. code-block:: yaml

    joe.bob:
      nexus3.user:
        - first_name: Joe
        - last_name: Bob
        - email: joe.bob@wherever.com
        - password: S3cr3tP4$$w0rd
        - roles:
          - repo-user

"""
# from __future__ import absolute_import, print_function, unicode_literals

import json
import logging

import requests

import nexus_groovy

log = logging.getLogger(__name__)


class _ScriptClient:
    """
    Class for working with the Nexus 3 scripts API
    """

    def __init__(self, host, username, password, script_name, script_data):
        self.host = host
        self.username = username
        self.password = password
        self.script_name = script_name
        self.script_data = script_data
        self.url = '{0}/service/rest/v1/script'.format(host)

    def delete(self):
        """
        Deletes script to Nexus 3 script API
        Returns false if script does not exist
        """
        delete_url = '{0}/{1}'.format(self.url, self.script_name)
        resp = False
        if self.get():
            log.debug('Deleting script: {0}'.format(self.script_name).format(self.script_name))
            req = requests.delete(delete_url, auth=(self.username, self.password))
            if req.status_code == 204 or 200:
                resp = req.content
                return resp
            log.error('Failed deleting script: {0} Reason: {1}'.format(self.script_name, req.status_code))

        return resp

    def get(self):
        """
        Get script to Nexus 3 script API
        Returns false if script does not exist
        """
        get_url = '{0}/{1}'.format(self.url, self.script_name)
        resp = False
        try:
            log.debug('Checking for script: {0}'.format(self.script_name))
            req = requests.get(get_url, auth=(self.username, self.password))
            if req.status_code == 204 or 200:
                resp = req.content
                return resp
            log.error('Failed checking for script: {0} Reason: {1}'.format(self.script_name, req.status_code))
        except Exception as e:
            log.error('Failed checking for script: {0} Reason: {1}'.format(self.script_name, e))

        return resp

    def list(self):
        req = requests.get(self.url, auth=(self.username, self.password))
        resp = req.content

        return resp

    def run(self, script_args):
        """
        Runs script to Nexus 3 script API
        Returns false if script does not exist

        Results returned as null from the script API
        is actually a positive in this case
        """
        run_url = '{0}/{1}/run'.format(self.url, self.script_name)
        headers = {'Content-Type': 'text/plain'}
        payload = json.dumps(script_args)

        resp = False
        if self.get():
            log.debug('Running script: {0}'.format(self.script_name))
            req = requests.post(run_url, auth=(self.username, self.password), headers=headers, data=payload)
            if req.status_code == 204 or 200:
                resp = req.json()
                return resp
            log.error('Failed running script: {0}" Reason: {1} {2}'.format(self.script_name, req.status_code, req.json()))

        return resp

    def upload(self):
        """
        Uploads script to Nexus 3 script API
        If a script of the same name already exists,
        it will be updated/replaced
        """

        data = {'name': self.script_name,
                'content': self.script_data,
                'type': 'groovy'}

        payload = json.dumps(data)

        headers = {'Content-Type': 'application/json'}
        resp = False
        if self.get():
            log.debug('Updating script: {0}'.format(self.script_name))
            upload_url = '{0}/{1}'.format(self.url, self.script_name)
            req = requests.put(upload_url, auth=(self.username, self.password), headers=headers, data=payload)
            if req.status_code == 204 or 200:
                resp = True
                return resp
            log.error('Failed updating script: {0} Reason: {1}'.format(self.script_name, req.status_code))
        else:
            log.debug('Uploading script: {0}'.format(self.script_name))
            req = requests.post(self.url, auth=(self.username, self.password), headers=headers, data=payload)
            if req.status_code == 204 or 200:
                resp = True
                return resp
            log.error('Failed uploading script "{0}." Reason: {1}'.format(self.script_name, req.status_code))

        return resp


def _connection_info():
    """
    Returns connection information used for the Nexus3 connection.
    """
    defaults = {'host': 'http://127.0.0.1:8081',
                'user': 'admin',
                'pass': 'admin123'}

    # return defaults
    connection_info = {}
    _opts = __salt__['config.option']('nexus3')
    default_addrs_used = []
    for attr in defaults:
        if attr not in _opts:
            default_addrs_used.append(attr)
            connection_info[attr] = defaults[attr]
            continue
        connection_info[attr] = _opts[attr]
    if default_addrs_used:
        log.info('Using default value for Nexus3: {0}'.format(default_addrs_used))
    return connection_info


def _script_processor(script_name, script_data, script_args, ret):
    connection_info = _connection_info()

    client = _ScriptClient(connection_info['host'],
                           connection_info['user'],
                           connection_info['pass'],
                           script_name,
                           script_data)

    upload_results = client.upload()

    if upload_results:
        run_results = client.run(script_args)
        if run_results:
            ret['changes'] = {'nexus': run_results['result']}
        else:
            ret['result'] = False
            ret['comment'] = 'Script: "{0}" failed to run.  See minion logs for details.'.format(script_name)
    else:
        ret['result'] = False
        ret['comment'] = 'Script: "{0}" failed to upload.  See minion logs for details.'.format(script_name)

    return ret


def allow_anonymous_access(name,
                           enable=False):
    """
    Enable or disable anonymous access to Nexus 3

    Args:
        name (str):
            This string can be completely random.
            It is not used anywhere except in the return message.
            It is only here because it is required by Salt
            and you can't use a boolean as the state id.
        enable (bool):
            True or False (default=False)
    Returns:
        str: AnonymousConfiguration{enabled=true, userId='anonymous', realmName='NexusAuthorizingRealm'}
             AnonymousConfiguration{enabled=false, userId='anonymous', realmName='NexusAuthorizingRealm'}
    """
    script_name = 'setup_anonymous_access'
    script_data = nexus_groovy.setup_anonymous_access

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run: {1}'.format(script_name, enable)}

    script_args = {'anonymous_access': enable}

    results = _script_processor(script_name, script_data, script_args, ret)
    return results


def base_url(name):
    """
    Enable or disable anonymous access to Nexus 3

    Args:
        name (str):
            URL to set base_url to for Nexus 3
            This would usually be the FQDN used
            to access Nexus
    Returns:
        str: 'null' if successful
    """
    script_name = 'setup_base_url'
    script_data = nexus_groovy.setup_base_url

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run to set base_url: {1}'.format(script_name, name)}

    script_args = {'base_url': name}

    results = _script_processor(script_name, script_data, script_args, ret)
    return results


def blobstore(name,
              path,
              store_type='file',
              s3_bucket='',
              s3_access_key_id='',
              s3_secret_access_key=''):
    """
    Enable or disable anonymous access to Nexus 3

    Args:
        name (str):
            Name of blobstore
        path (str):
            full folder path for blobstore. This is
            typically the Nexus data directory + '/blobs/<name of blobstore>'
        store_type (str):
            Optional: Type of blobstore
            Options = File or S3 (default=file)
        s3_bucket (str):
            Optional: Name of S3 bucket
        s3_access_key_id (str):
            Optional: AWS Access Key for S3 bucket
        s3_secret_access_key (str):
            Optional: AWS Secret Access Key for S3 bucket
    Returns:
        str: 'null' if successful
    """
    script_name = 'create_blobstore'
    script_data = nexus_groovy.create_blobstore

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run for blobstore: {1}'.format(script_name, name)}

    s3_config = {'s3_bucket': s3_bucket,
                 's3_access_key_id': s3_access_key_id,
                 's3_secret_access_key': s3_secret_access_key}

    script_args = {'name': name,
                   'path': path,
                   'type': store_type,
                   'config': s3_config}

    results = _script_processor(script_name, script_data, script_args, ret)
    return results


def email_server(name,
                 email_server_port,
                 email_server_enabled=True,
                 email_server_username=None,
                 email_server_password=None,
                 email_from_address='nexus@example.org',
                 email_subject_prefix='Nexus: ',
                 email_tls_enabled=True,
                 email_tls_required=False,
                 email_ssl_on_connect_enabled=True,
                 email_ssl_check_server_identity_enabled=True,
                 email_trust_store_enabled=False):
    """
    Setup SMTP servers for Nexus to send emails through

    Args:
        name (str):
            Hostname or IP address of SMTP server
        email_server_enabled (bool):
            Enable email server
            Options: True or False (default=True)
        email_server_port (int):
            Port of SMTP server
        email_server_username (str):
            Username for SMTP server (default=None)
        email_server_password (str):
            Password for SMTP servers (default=None)
        email_from_address (str):
            Set from address for emails from Nexus (default='nexus@example.org')
        email_subject_prefix (str):
            Set subject prefix for emails from Nexus (default='Nexus: '
        email_tls_enabled (bool):
            Enable STARTTLS support for insecure connections (default=True)
        email_tls_required (bool):
            Require STARTTLS support (default=False)
        email_ssl_on_connect_enabled (bool):
            Enable SSL/TLS encryption upon connection (default=True)
        email_ssl_check_server_identity_enabled (bool):
            Enable server identity check (default=True)
        email_trust_store_enabled (bool):
            Use certificates stored in the Nexus truststore to connect to external systems (default=False)

    """
    script_name = 'setup_email'
    script_data = nexus_groovy.setup_email

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run for core configurations: {1}'.format(script_name, name)}

    script_args = {'email_server_host': name,
                   'email_server_enabled': email_server_enabled,
                   'email_server_port': email_server_port,
                   'email_server_username': email_server_username,
                   'email_server_password': email_server_password,
                   'email_from_address': email_from_address,
                   'email_subject_prefix': email_subject_prefix,
                   'email_tls_enabled': email_tls_enabled,
                   'email_tls_required': email_tls_required,
                   'email_ssl_on_connect_enabled': email_ssl_on_connect_enabled,
                   'email_ssl_check_server_identity_enabled': email_ssl_check_server_identity_enabled,
                   'email_trust_store_enabled': email_trust_store_enabled}

    results = _script_processor(script_name, script_data, script_args, ret)
    return results


def realms(name,
           status):
    """
    Enable or disable authentication realms in Nexus
    Args:
        name (str):
            Name of realm
            Options: NuGetApiKey, NpmToken, rutauth-realm, LdapRealm, DockerToken
        status (bool):
            Enable or disable realm
            Options: True or false
    Returns:
        str: 'null' if successful
    """

    script_name = 'setup_realms'
    script_data = nexus_groovy.setup_realms

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run for realm: {1}'.format(script_name, name)}

    script_args = {'realm_name': name,
                   'status': status}

    results = _script_processor(script_name, script_data, script_args, ret)

    return results


def repo_group(name,
               repo_type,
               member_repos,
               docker_http_port=None,
               docker_force_basic_auth=True,
               docker_v1_enabled=False,
               blob_store='default',
               strict_content_validation=True):
    """
    Create or modify Nexus 3 hosted repository
    Args:
        name (str):
            A unique identifier for this repository
        repo_type (str):
            Type of repo
            Options: yum,npm,raw,pypi,nuget,rubygems,docker,bower
        member_repos (list):
            List of repos to include in group.  Nexus will only add repos of the same
            type (ie only maven repos can be added to a maven group)
        docker_http_port (int):
            Optional: port for docker registry to listen on
        docker_force_basic_auth (bool):
            Optional: Force basic authentication for docker pull
            Options: True or False (default=True)
        docker_v1_enabled (bool):
            Optional: Allow clients to use the V1 API to interact with this Repository
            Options: True or False (default=False)
        blob_store (list):
            Optional: Blob store used to store asset content (default='default')
        strict_content_validation (bool):
            Optional: Validate that all content uploaded to this repository is of a MIME type appropriate
            for the repository format (default=True)

    """
    script_name = 'create_repo_group'
    script_data = nexus_groovy.create_repo_group

    recipe_name = {'docker': 'docker-group',
                   'maven': 'maven2-group',
                   'bower': 'bower-group',
                   'npm': 'npm-group',
                   'pypi': 'pypi-group',
                   'rubygems': 'rubygems-group',
                   'yum': 'yum-group',
                   'raw': 'raw-group'}[repo_type]

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run for repo: {1}'.format(script_name, name)}

    script_args = {'name': name,
                   'recipe_name': recipe_name,
                   'member_repos': member_repos,
                   'docker_http_port': docker_http_port,
                   'docker_v1_enabled': docker_v1_enabled,
                   'docker_force_basic_auth': docker_force_basic_auth,
                   'blob_store': blob_store,
                   'strict_content_validation': strict_content_validation}

    results = _script_processor(script_name, script_data, script_args, ret)

    return results


def repo_hosted(name,
                repo_type,
                docker_http_port=None,
                docker_force_basic_auth=True,
                docker_v1_enabled=False,
                maven_version_policy='release',
                maven_layout_policy='permissive',
                yum_repodata_depth=0,
                yum_deploy_policy='strict',
                write_policy='allow',
                blob_store='default',
                strict_content_validation=True):
    """
    Create or modify Nexus 3 hosted repository
    Args:
        name (str):
            A unique identifier for this repository
        repo_type (str):
            Type of repo
            Options: yum,npm,raw,pypi,nuget,rubygems,docker,bower
        docker_http_port (int):
            Optional: port for docker registry to listen on
        docker_force_basic_auth (bool):
            Optional: Force basic authentication for docker pull
            Options: True or False (default=True)
        docker_v1_enabled (bool):
            Optional: Allow clients to use the V1 API to interact with this Repository
            Options: True or False (default=False)
        maven_version_policy (str):
            Optional: Specify which type of marven artificats this repository stores
            Options: release, snapshot, mixed (default=release)
        maven_layout_policy (str):
            Optional: Validate hat all paths are maven artifacts or metadata paths
            Options: strict or permissive (default=permissive)
        yum_repodata_depth (int):
            Optional: Specifies the repository depth where repodata folder(s) are created (default=0)
        yum_deploy_policy (str):
            Optional: Validate that all paths are RPMs or yum metadata
            Options: strict or permissive (default=strict)
        write_policy (str):
            Optional: Controls if deployments of and updates to artifacts are allowed
            Options: allow, allow_once, deny (default=allow)
        blob_store (list):
            Optional: Blob store used to store asset content (default='default')
        strict_content_validation (bool):
            Optional: Validate that all content uploaded to this repository is of a MIME type appropriate
            for the repository format (default=True)
    Returns:
        str: RepositoryImpl$$EnhancerByGuice$$dc09c205{type=hosted, format=<repo format>, name='<name of repo>'} if
            successful
    """
    script_name = 'create_repo_hosted'
    script_data = nexus_groovy.create_repo_hosted

    recipe_name = {'docker': 'docker-hosted',
                   'maven': 'maven2-hosted',
                   'bower': 'bower-hosted',
                   'npm': 'npm-hosted',
                   'pypi': 'pypi-hosted',
                   'rubygems': 'rubygems-hosted',
                   'yum': 'yum-hosted',
                   'raw': 'raw-hosted'}[repo_type]

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run for repo: {1}'.format(script_name, name)}

    script_args = {'name': name,
                   'recipe_name': recipe_name,
                   'docker_http_port': docker_http_port,
                   'docker_v1_enabled': docker_v1_enabled,
                   'docker_force_basic_auth': docker_force_basic_auth,
                   'maven_version_policy': maven_version_policy,
                   'maven_layout_policy': maven_layout_policy,
                   'yum_repodata_depth': yum_repodata_depth,
                   'yum_deploy_policy': yum_deploy_policy,
                   'write_policy': write_policy,
                   'blob_store': blob_store,
                   'strict_content_validation': strict_content_validation}

    results = _script_processor(script_name, script_data, script_args, ret)

    return results


def repo_proxy(name,
               repo_type,
               remote_url,
               docker_http_port=None,
               docker_force_basic_auth=True,
               docker_v1_enabled=False,
               maven_version_policy='release',
               maven_layout_policy='permissive',
               content_max_age=1440.0,
               metadata_max_age=1440.0,
               docker_index_type='registry',
               docker_use_nexus_certificates_to_access_index=False,
               blob_store='default',
               strict_content_validation=True,
               remote_username=None,
               remote_password=None):
    """
    Create or modify Nexus 3 proxy repository
    Args:
        name (str):
            A unique identifier for this repository
        repo_type (str):
            Type of repo
            Options: yum,npm,raw,pypi,nuget,rubygems,docker,bower
        remote_url (str):
            Location of the remote repository being proxied
        docker_http_port (int):
            Optional: port for docker registry to listen on
        docker_force_basic_auth (bool):
            Optional: Force basic authentication for docker
            Options: True or False (default=True)
        docker_v1_enabled (bool):
            Optional: Allow clients to use the V1 API to interact with this Repository
            Options: True or False (default=False)
        maven_version_policy (str):
            Optional: Specify which type of marven artificats this repository stores
            Options: release, snapshot, mixed (default=release)
        maven_layout_policy (str):
            Optional: Validate hat all paths are maven artifacts or metadata paths
            Options: strict or permissive (default=permissive)
        content_max_age (int):
            Optional: How long (in minutes) to cache artifacts before rechecking the
            remote repository. Release repositories should use -1 (default=1440)
        metadata_max_age (int):
            Optional: How long (in minutes) to cache metadata before rechecking the
            remote repository. (default=1440)
        docker_index_type (str):
            Optional: Specify location of docker index
            Options: registry or hub (default=registry)
        docker_use_nexus_certificates_to_access_index (bool):
            Optional: Specify to use Nexus certificate store
            Options: True or False (default=False)
        blob_store (list):
            Optional: Blob store used to store asset content (default='default')
        strict_content_validation (bool):
            Optional: Validate that all content uploaded to this repository is of a MIME type appropriate
            for the repository format (default=True)
        remote_username (str):
            Optional: username if remote_url requires authentication
        remote_password (str):
            Optional: passoword if remote_url requires authentication
    Returns:
        str: RepositoryImpl$$EnhancerByGuice$$dc09c205{type=proxy, format=<repo format>, name='<name of repo>'} if
            successful
    """
    script_name = 'create_repo_proxy'
    script_data = nexus_groovy.create_repo_proxy

    recipe_name = {'docker': 'docker-proxy',
                   'maven': 'maven2-proxy',
                   'bower': 'bower-proxy',
                   'npm': 'npm-proxy',
                   'pypi': 'pypi-proxy',
                   'rubygems': 'rubygems-proxy',
                   'yum': 'yum-proxy',
                   'raw': 'raw-proxy'}[repo_type]

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run for repo: {1}'.format(script_name, name)}

    script_args = {'name': name,
                   'recipe_name': recipe_name,
                   'docker_http_port': docker_http_port,
                   'docker_v1_enabled': docker_v1_enabled,
                   'docker_force_basic_auth': docker_force_basic_auth,
                   'maven_version_policy': maven_version_policy,
                   'maven_layout_policy': maven_layout_policy,
                   'remote_url': remote_url,
                   'content_max_age': content_max_age,
                   'metadata_max_age': metadata_max_age,
                   'docker_index_type': docker_index_type,
                   'docker_use_nexus_certificates_to_access_index': docker_use_nexus_certificates_to_access_index,
                   'blob_store': blob_store,
                   'strict_content_validation': strict_content_validation,
                   'remote_username': remote_username,
                   'remote_password': remote_password}

    results = _script_processor(script_name, script_data, script_args, ret)

    return results

    
def role(name,
         description,
         privileges,
         base_roles):
    """
    Create or modify Nexus 3 user roles

    Args:
        name (str):
            used for the id and name of the role
        description (str):
            desription of the role
        privileges (list):
            list of privileges applied to role
        base_roles (list):
            list of role(s) for new role.
            this is required for some reason I don't understand
    Returns:
        str: 'null' if successful
    """
    script_name = 'setup_role'
    script_data = nexus_groovy.setup_role

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run for role: {1}'.format(script_name, name)}

    script_args = {'id': name,
                   'name': name,
                   'description': description,
                   'privileges': privileges,
                   'roles': base_roles}

    results = _script_processor(script_name, script_data, script_args, ret)

    return results


def task(name,
         task_type_id,
         task_properties,
         task_cron,
         task_alert_email=None):
    """
    Args:
        name (str):
            Name of task
        task_type_id (str):
            Nexus taskId
            Options: db.backup, repository.docker.gc, repository.docker.upload-purge,
                     blobstore.compact, repository.purge-unused
        task_properties (dict):
            Dictionary of the task properties
        task_alert_email (str):
            Email to send alerts to
        task_cron (str):
            Options: '0 0 11 * 5 ?'

            Field Name	Allowed Values
            Seconds	    0-59
            Minutes	    0-59
            Hours	    0-23
            Dayofmonth	1-31
            Month	    1-12 or JAN-DEC
            Dayofweek	1-7 or SUN-SAT
            Year(optional)	empty, 1970-2099
    Returns:
        str: metadata about task if successful
    """

    script_name = 'create_task'
    script_data = nexus_groovy.create_task

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run for role: {1}'.format(script_name, name)}

    script_args = {'name': name,
                   'typeId': task_type_id,
                   'taskProperties': task_properties,
                   'task_alert_email': task_alert_email,
                   'cron': task_cron}

    results = _script_processor(script_name, script_data, script_args, ret)

    return results


def user(name,
         first_name,
         last_name,
         email,
         password,
         roles):
    """
    Create or modify Nexus 3 user

    Args:
        name (str):
            The username for user
        first_name (str):
            First name of user
        last_name (str):
            Last name of user
        email (str):
            Email address of user.  Technically required by Nexus, but the user will
            still be created without
        password (str):
            Password for user
        roles (list):
            List of user roles.  User roles need to exist or be create first
    Returns:
        str: 'null' if successful
    """
    script_name = 'setup_user'
    script_data = nexus_groovy.setup_user

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': '"{0}" script run for user: {1}'.format(script_name, name)}

    script_args = {'username': name,
                   'first_name': first_name,
                   'last_name': last_name,
                   'email': email,
                   'password': password,
                   'roles': roles}

    results = _script_processor(script_name, script_data, script_args, ret)

    return results
