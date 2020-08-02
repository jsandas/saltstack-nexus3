nexus:
  blobstores:
    docker: []
    raw:
      - quota_type: spaceRemainingQuota
      - quota_limit: 1000000000
    yum: []
    unwanted-blobstore:
      - quota_type: spaceRemainingQuota
      - quota_limit: 1000000000
  privileges:
    repo-admin:
      - actions: ['ALL']
      - description: 'test repo admin'
      - format: maven2
      - repository: '*'
      - type: repository-admin
    unwanted-privilege:
      - actions: ['ALL']
      - description: 'unwanted privilege'
      - format: maven2
      - repository: '*'
      - type: repository-admin
  repositories:
    some-yum-proxy:
      - format: yum
      - type: proxy
      - remote_url: https://rpm.somerepo.com/
      - blobstore: yum
      - remote_username: username
      - remote_password: password
    some-yum-group:
      - format: yum
      - type: group
      - group_members: ['some-yum-proxy']
      - strict_content_validation: False
    hosted-docker:
      - format: docker
      - type: hosted
      - blobstore: docker
      - docker_http_port: 5000
    hosted-unwanted:
      - format: yum
      - type: hosted
      - blobstore: yum
  roles:
    repo-admin:
      - privileges: ['nx-repository-view-*-*-*']
      - description: 'role with privileges to administer repositories'
      - roles: ['nx-anonymous']
    repo-user:
      - privileges: ['nx-repository-view-*-*-read']
      - description: 'role with privileges to read repositories'
      - roles: ['nx-anonymous']
    unwanted-role:
      - privileges: ['nx-repository-view-*-*-read']
      - description: 'unwanted rolewith privileges to read repositories'
      - roles: ['nx-anonymous']
  tasks:
    database_backup:
      typeId: 'db.backup'
      taskProperties: 
        location: '/nexus-data/backup'
      cron: '0 0 21 * * ?'
    docker-garbage-collection:
      typeId: repository.docker.gc
      taskProperties:
        repositoryName: '*'
      cron: '0 0 11 * * ?'
    docker-compact-blobstore:
      typeId: blobstore.compact
      taskProperties:
        blobstoreName: 'docker'
      cron: '0 0 13 * * ?'
  users:
    repo-admin:
      - firstName: Repo
      - lastName: Admin
      - emailAddress: repo-admin@nowhere.com
      - roles: ['repo-admin']
      - password: 'S3cr3tP4ssw0rd1'
    repo-user:
      - firstName: Repo
      - lastName: User
      - emailAddress: repo-user@nowhere.com
      - roles: ['repo-user']
      - password: 'S3cr3tP4ssw0rd2'
    unwanted-user:
      - firstName: Unwanted
      - lastName: User
      - emailAddress: unwanted-user@nowhere.com
      - roles: ['nx-anonymous']
      - password: 'S3cr3tP4ssw0rd3'
