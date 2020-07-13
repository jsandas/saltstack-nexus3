nexus:
  blobstores:
    yum: []
    raw:
      - quota_type: spaceRemainingQuota
      - quota_limit: 1000000000

  privileges:
    repo-admin:
      - actions: ['ALL']
      - description: 'Test repo admin'
      - format: maven2
      - repository: '*'
      - privilege_type: repository-admin
  repositories:
    some-yum-repo:
      - repo_format: yum
      - repo_type: proxy
      - remote_url: https://rpm.somerepo.com/
      - blobstore: yum
      - remote_username: username
      - remote_password: password
    some-yum-group:
      - repo_format: yum
      - repo_type: group
      - group_members: ['some-yum-repo']
      - strict_content_validation: False
    hosted-docker:
      - repo_format: docker
      - repo_type: hosted
      - blobstore: docker
      - docker_http_port: 5000
  roles:
    repo-admin:
      - privileges: ['nx-repository-view-*-*-*']
      - description: 'User with privileges to administer repositories'
      - roles: ['nx-anonymous']
    repo-user:
      - privileges: ['nx-repository-view-*-*-read']
      - description: 'User with privileges to read repositories'
      - roles: ['nx-anonymous']
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
  tasks:
    database-backup:
      task_type_id: 'db.backup'
      task_properties:
        location: '/nexus-data/backup'
      task_cron: '0 0 21 * * ?'

