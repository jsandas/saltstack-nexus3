nexus:
  roles:
    repo-admin:
      name: 'Repo Admin'
      privileges: ['nx-repository-view-*-*-*']
      description: 'User with privileges to administer repositories'
      base_roles: ['nx-anonymous']
    repo-user:
      name: 'Repo User'
      privileges: ['nx-repository-view-*-*-read']
      description: 'User with privileges to read repositories'
      base_roles: ['nx-anonymous']
  users:
    repo-admin:
      first_name: Repo
      last_name: Admin
      email: repo-admin@nowhere.com
      roles: ['repo-admin']
      password: 'S3cr3tP4ssw0rd1'
    repo-user:
      first_name: Repo
      last_name: User
      email: repo-user@nowhere.com
      roles: ['repo-user']
      password: 'S3cr3tP4ssw0rd2'
  tasks:
    database-backup:
      task_type_id: 'db.backup'
      task_properties:
        location: '/nexus-data/backup'
      task_cron: '0 0 21 * * ?'
  repos:
    proxy:
      some-yum-repo:
        - repo_type: yum
        - remote_url: https://rpm.somerepo.com/
        - blob_store: yum
        - remote_username: username
        - remote_password: password
    hosted:
      hosted-docker:
        - repo_type: docker
        - blob_store: docker
        - docker_http_port: 5000
