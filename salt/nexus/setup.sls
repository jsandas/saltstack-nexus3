{% from "nexus/map.jinja" import nexus with context %}

{% for role, data in nexus['roles'].items() %}
{{ role }}:
  nexus3.role:
    - description: '{{ data.description }}'
    - privileges:
      - nx-repository-view-*-*-read
    - base_roles: 
      - {{ data.base_roles }}
{% endfor %}

test_user:
  nexus3.user:
    - name: joe.job
    - first_name: joe
    - last_name: bob
    - email: test@nowhere.com
    - password: 'testing123'
    - base_roles:
      - repo-user

enable_anonymous_access:
  nexus3.allow_anonymous_access:
    - enable: True

http://localhost:8081:
  nexus3.base_url

yum:
  nexus3.blobstore:
    - path: /nexus-data/blobs/yum

docker-test:
  nexus3.repo_proxy:
    - repo_type: docker
    - docker_http_port: 5000
    - docker_force_basic_auth: False
    - remote_url: 'http://mirrors.centos.org/7/x86_64'
    - strict_content_validation: True
    - remote_username: testing
    - remote_password: testing123

yum-test:
  nexus3.repo_proxy:
    - repo_type: yum
    - remote_url: 'http://mirrors.centos.org/7/x86_64'
    - strict_content_validation: True
    - blob_store: yum

maven-test:
  nexus3.repo_proxy:
    - repo_type: maven
    - remote_url: 'http://mirrors.centos.org/7/x86_64'
    - strict_content_validation: True
    - maven_version_policy: snapshot
    - maven_layout_policy: strict

pypi-test:
  nexus3.repo_proxy:
    - repo_type: pypi
    - remote_url: 'http://mirrors.centos.org/7/x86_64'
    - strict_content_validation: False
    - remote_username: testingpypi
    - remote_password: testing123

npm-test:
  nexus3.repo_proxy:
    - repo_type: npm
    - remote_url: 'http://mirrors.centos.org/7/x86_64'
    - strict_content_validation: True

bower-test:
  nexus3.repo_proxy:
    - repo_type: bower
    - remote_url: 'http://mirrors.centos.org/7/x86_64'
    - strict_content_validation: True

maven-hosted:
  nexus3.repo_hosted:
    - repo_type: maven
    - write_policy: allow_once
    - blob_store: default
    - maven_version_policy: release
    - maven_layout_policy: strict
    - strict_content_validation: True 

yum-host:
  nexus3.repo_hosted:
    - repo_type: yum
    - yum_repodata_depth: 0
    - yum_deploy_policy:  permissive
    - strict_content_validation: True
  
docker-host:
  nexus3.repo_hosted:
    - repo_type: docker
    - docker_http_port: 5001
    - docker_force_basic_auth: False
    - docker_v1_enabled: True
    - strict_content_validation: True

pypi-host:
  nexus3.repo_hosted:
    - repo_type: pypi
    - strict_content_validation: False
    - write_policy: allow

maven-group:
  nexus3.repo_group:
    - repo_type: maven
    - member_repos:
      - maven-central
      - maven-hosted
      - maven-public
      - npm-test
    - strict_content_validation: True

docker-group:
  nexus3.repo_group:
    - repo_type: docker
    - docker_http_port: 5010
    - docker_force_basic_auth: True
    - member_repos:
      - docker-host
      - docker-test
    - strict_content_validation: True

enable_docker_realm:
  nexus3.realms:
    - name: DockerToken
    - status: True

database_backup:
  nexus3.tasks:
    - task_type_id: 'db.backup'
    - task_properties: 
        location: '/nexus-data/backup'
    - task_cron: '0 0 21 * * ?'