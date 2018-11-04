State files for setting up Nexus 3 using docker and State module for working with the Nexus 3 API to configure Nexus.  This is a work in progress.

Installation:
Copy the _states folder the the files_root on the saltmaster (usually '/srv/salt').  Then run saltutil.sync_states or saltutil.sync_all to copy the files to the minion.

    Example:
        salt '*' saltutil.sync_states

The files in the nexus folder as well as the pillar data can be used as examples for using this state module.

These example files will create the local user and directory for Nexus and download/start the docker container.  Feel free to adapt to your needs.  It is recommended to use a reverse proxy in front of Nexus for SSL termination.

This state module leverages the ThoTeam's work for Ansible: https://github.com/ansible-ThoTeam/nexus3-oss.
The groovy scripts used by this state are copied to or adapted for using with salt and provided in a python file as strings to keep things simple for maintaining the salt state..

The nexus3 state module depends on python requests library which should already be installed when the salt minion was installed.

Configuration:
In order to connect to Nexus 3, credentials can be provided through the minion configuration in yaml format:

    nexus3:
      host: '127.0.0.1:8081'
      user: 'admin'
      pass: 'admin123'

If no credentials are provided in the minion configuration file, the defaults for Nexus 3 are used instead.

TODO:
Update README with more descriptions and examples of other functions


  salt.states.nexus3.**allow_anonymous_access**(name,enable=False):

    Enable or disable anonymous access to Nexus 3

    name (str):
        This string can be completely random.
        It is not used anywhere except in the return message.
        It is only here because it is required by Salt
        and you can't use a boolean as the state id.
    enable (bool):
        True or False (default=False)

    Example:

      allow_anonymous_access:
        nexus3.allow_anonymous_access:
          - option: False


  salt.states.nexus3.**base_url**(name):

    Enable or disable anonymous access to Nexus 3

    name (str):
        URL to set base_url to for Nexus 3
        This would usually be the FQDN used
        to access Nexus

    Example:

      http://localhost:8081:
        nexus3.base_url


  salt.states.nexus3.**blobstore**(name,path,store_type='file',s3_bucket='',s3_access_key_id='',s3_secret_access_key=''):

    Enable or disable anonymous access to Nexus 3

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

    Example:

      raw:
        nexus3.blobstore:
          - path: /nexus-data/blobs/raw


  salt.states.nexus3.**email_server**(name,email_server_port,email_server_enabled=True,email_server_username=None,email_server_password=None,email_from_address='nexus@example.org',email_subject_prefix='Nexus: ',email_tls_enabled=True,email_tls_required=False,email_ssl_on_connect_enabled=True,email_ssl_check_server_identity_enabled=True,email_trust_store_enabled=False):

    Setup SMTP server for Nexus to send emails through

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
        Password for SMTP server (default=None)
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

    Example:

    TODO: make example


  salt.states.nexus3.**realms**(name,status):

    Enable or disable authentication realms in Nexus

    name (str):
        Name of realm
        Options: NuGetApiKey, NpmToken, rutauth-realm, LdapRealm, DockerToken
    status (bool):
        Enable or disable realm
        Options: True or false

    Example:

      enable_docker_realm:
        nexus3.realms:
          - name: DockerToken
          - status: True


  salt.states.nexus3.**repo_group**(name,repo_type,member_repos,docker_http_port=None,docker_force_basic_auth=True,docker_v1_enabled=False,blob_store='default',strict_content_validation=True):

    Create or modify Nexus 3 hosted repository group

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

  Example:

    maven-group:
      nexus3.repo_group:
        - repo_type: maven
        - member_repo:
          - maven-central
          - maven-local
        - strict_content_validation: True


  salt.states.nexus3.**repo_hosted**(name,repo_type,docker_http_port=None,docker_force_basic_auth=True,docker_v1_enabled=False,maven_version_policy='release',maven_layout_policy='permissive',yum_repodata_depth=0,yum_deploy_policy='strict',write_policy='allow',blob_store='default',strict_content_validation=True):

    Create or modify Nexus 3 hosted repository

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

  Example:

    maven-hosted:
      nexus3.repo_hosted:
        - repo_type: maven
        - blob_store: default
        - maven_version_policy: RELEASE
        - maven_layout_policy: STRICT
        - strict_content_validation: True


  salt.states.nexus3.**repo_proxy**(name,repo_type,remote_url,docker_http_port=None,docker_force_basic_auth=True,docker_v1_enabled=False,maven_version_policy='release',maven_layout_policy='permissive',content_max_age=1440.0,metadata_max_age=1440.0,docker_index_type='registry',docker_use_nexus_certificates_to_access_index=False,blob_store='default',strict_content_validation=True,remote_username=None,remote_password=None):

    Create or modify Nexus 3 proxy repository

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

  Example:
  Note: This example assumes a blob_store names "yum" already exists

    yum-proxy:
      nexus3.repo_proxy:
        - type: yum
        - remote_url: 'http://mirrors.centos.org/7/x86_64'
        - blob_store: yum
        - strict_content_validation: True


  salt.states.nexus3.**role**(name,description,privileges,base_roles):

    Create or modify Nexus 3 user roles

    name (str):
        used for the id and name of the role
    description (str):
        desription of the role
    privileges (list):
        list of privileges applied to role
    base_roles (list):
        list of role(s) for new role.
        this is required for some reason I don't understand

  Example:

    repo-user:
      nexus3.role:
        - description: 'Read only user'
        - privileges:
          - nx-repository-view-*-*-read
        - roles:
          - repo-user


  salt.states.nexus3.**task**(name,task_type_id,task_properties,task_cron,task_alert_email=None):
    
    Create or modify scheduled task in Nexus 3

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
        Options: '0 0 11 * 5 ?
        Field Name	Allowed Values
        Seconds	    0-59
        Minutes	    0-59
        Hours	    0-23
        Dayofmonth	1-31
        Month	    1-12 or JAN-DEC
        Dayofweek	1-7 or SUN-SAT
        Year(optional)	empty, 1970-2099

    Example:
    Note: The key/values under task_properties is indented 4 spaces instead
    of two.  This is how salt creates a dictionary from the yaml

      database_backup:
        nexus3.tasks:
          - task_type_id: 'db.backup'
          - task_properties:
              location:'/nexus-data/backup'
          - task_cron: '0 0 21 * * ?'


  salt.states.nexus3.**user**(name,first_name,last_name,email,password,roles):

    Create or modify Nexus 3 user

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

    Example:
    Note: role(s) must exist first

      joe.bob:
        nexus3.user:
          - first_name: Joe
          - last_name: Bob
          - email: joe.bob@wherever.com
          - password: S3cr3tP4$$w0rd
          - roles:
            - repo-user
