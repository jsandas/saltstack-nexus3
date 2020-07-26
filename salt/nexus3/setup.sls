{% from tpldir + "/map.jinja" import nexus with context %}

# burgers_create:
#   nexus3_blobstores.present:
#     - name: burgers

# burgers_update:
#   nexus3_blobstores.present:
#     - name: burgers
#     - quota_type: spaceRemainingQuota
#     - quota_limit: 5000000

# burgers_delete:
#   nexus3_blobstores.absent:
#     - name: burgers

# # should not exist
# delete_test_blobstore:
#   nexus3_blobstores.absent:
#     - name: test



# clear_email:
#   nexus3_email.clear
  
# yum-proxy:
#   nexus3_repositories.present:
#     - repo_format: yum
#     - repo_type: proxy
#     - remote_url: http://mirror.centos.org/centos/7/os/x86_64/
#     - content_max_age: 3600

# create-yum-hosted:
#   nexus3_repositories.present:
#     - name: yum-hosted
#     - repo_format: yum
#     - repo_type: hosted
#     - yum_repodata_depth: 0
#     - yum_deploy_policy:  permissive
#     - strict_content_validation: True

# delete-yum-hosted:
#   nexus3_repositories.absent:
#     - name: yum-hosted

# nonexistent-repo:
#   nexus3_repositories.absent

# set_anonymous_access_false:
#   nexus3_security.anonymous_access:
#     - enabled: False

# create_privilege:
#   nexus3_privileges.present:
#     - name: testing1
#     - actions: ['ALL']
#     - description: 'Test repo admin'
#     - format: maven2
#     - repository: '*'
#     - privilege_type: repository-admin

# delete_privilege:
#   nexus3_privileges.absent:
#     - name: testing1

# create_role:
#   nexus3_roles.present:
#     - name: testing1
#     - description: 'test role'
#     - privileges: ['nx-repository-view-*-*-read']
#     - roles: ['nx-anonymous']

# update_role:
#   nexus3_roles.present:
#     - name: testing1
#     - description: 'test role update'
#     - privileges: ['nx-repository-view-*-*-read']
#     - roles: ['nx-anonymous']

# create_user1:
#   nexus3_users.present:
#     - name: test_user1 
#     - password: abc123
#     - emailAddress: test@email.com
#     - firstName: Test1
#     - lastName: User
#     - roles: ['nx-admin']

# create_user2:
#   nexus3_users.present:
#     - name: test_user2
#     - password: abc123
#     - emailAddress: test@email.com
#     - firstName: Test2
#     - lastName: User
#     - roles: ['testing1']

# # states based on pillar data
# {% for blobstore, data in nexus['blobstores'].items() %}
# create_blobstore_{{ blobstore }}:
#   nexus3_blobstores.present:
#     - name: {{ blobstore }}
#   {% for item in data %}
#     - {{ item }}
#   {% endfor %}
# {% endfor %}

set_anonymous_access_true:
  nexus3_security.anonymous_access:
    - enabled: True

update_realms:
  nexus3_security.realms:
    - realms: 
      - NexusAuthenticatingRealm
      - NexusAuthorizingRealm
      - DockerToken

setup_email:
  nexus3_email.configure:
    - enabled: True
    - host: smtp.example.com
    - port: 587
    - fromAddress: test@example.com
    - startTlsEnabled: True

{% for privilege, data in nexus['privileges'].items() %}
create_privilege_{{ privilege }}:
  nexus3_privileges.present:
    - name: {{ privilege }}
  {% for item in data %}
    - {{ item }}
  {% endfor %}
{% endfor %}

# {% for repository, data in nexus['repositories'].items() %}
# repositories_{{ repository }}:
#   nexus3_repositories.present:
#     - name: {{ repository }}
#   {% for item in data %}
#     - {{ item }}
#   {% endfor %}
# {% endfor %}

{% for role, data in nexus['roles'].items() %}
role_{{ role }}:
  nexus3_roles.present:
    - name: {{ role }}
  {% for item in data %}
    - {{ item }}
  {% endfor %}
{% endfor %}

{% for user, data in nexus['users'].items() %}
user_{{ user }}:
  nexus3_users.present:
    - name: {{ user }}
  {% for item in data %}
    - {{ item }}
  {% endfor %}
{% endfor %}

# http://localhost:8081:
#   nexus3.base_url

# docker-test:
#   nexus3.repo_proxy:
#     - repo_type: docker
#     - docker_http_port: 5000
#     - docker_force_basic_auth: False
#     - remote_url: 'http://mirrors.centos.org/7/x86_64'
#     - strict_content_validation: True
#     - remote_username: testing
#     - remote_password: testing123

# yum-test:
#   nexus3.repo_proxy:
#     - repo_type: yum
#     - remote_url: 'http://mirrors.centos.org/7/x86_64'
#     - strict_content_validation: True
#     - blob_store: yum

# maven-test:
#   nexus3.repo_proxy:
#     - repo_type: maven
#     - remote_url: 'http://mirrors.centos.org/7/x86_64'
#     - strict_content_validation: True
#     - maven_version_policy: snapshot
#     - maven_layout_policy: strict

# pypi-test:
#   nexus3.repo_proxy:
#     - repo_type: pypi
#     - remote_url: 'http://mirrors.centos.org/7/x86_64'
#     - strict_content_validation: False
#     - remote_username: testingpypi
#     - remote_password: testing123

# npm-test:
#   nexus3.repo_proxy:
#     - repo_type: npm
#     - remote_url: 'http://mirrors.centos.org/7/x86_64'
#     - strict_content_validation: True

# bower-test:
#   nexus3.repo_proxy:
#     - repo_type: bower
#     - remote_url: 'http://mirrors.centos.org/7/x86_64'
#     - strict_content_validation: True

# maven-hosted:
#   nexus3.repo_hosted:
#     - repo_type: maven
#     - write_policy: allow_once
#     - blob_store: default
#     - maven_version_policy: release
#     - maven_layout_policy: strict
#     - strict_content_validation: True 

# yum-host:
#   nexus3.repo_hosted:
#     - repo_type: yum
#     - yum_repodata_depth: 0
#     - yum_deploy_policy:  permissive
#     - strict_content_validation: True
  
# docker-host:
#   nexus3.repo_hosted:
#     - repo_type: docker
#     - docker_http_port: 5001
#     - docker_force_basic_auth: False
#     - docker_v1_enabled: True
#     - strict_content_validation: True

# pypi-host:
#   nexus3.repo_hosted:
#     - repo_type: pypi
#     - strict_content_validation: False
#     - write_policy: allow

# maven-group:
#   nexus3.repo_group:
#     - repo_type: maven
#     - member_repos:
#       - maven-central
#       - maven-hosted
#       - maven-public
#       - npm-test
#     - strict_content_validation: True

# docker-group:
#   nexus3.repo_group:
#     - repo_type: docker
#     - docker_http_port: 5010
#     - docker_force_basic_auth: True
#     - member_repos:
#       - docker-host
#       - docker-test
#     - strict_content_validation: True

# enable_docker_realm:
#   nexus3.realms:
#     - name: DockerToken
#     - status: True

# database_backup:
#   nexus3.tasks:
#     - task_type_id: 'db.backup'
#     - task_properties: 
#         location: '/nexus-data/backup'
#     - task_cron: '0 0 21 * * ?'