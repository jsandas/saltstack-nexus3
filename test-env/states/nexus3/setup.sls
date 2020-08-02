{% from tpldir + "/map.jinja" import nexus with context %}

set_anonymous_access_true:
  nexus3_security.anonymous_access:
    - enabled: True

update_realms:
  nexus3_security.realms:
    - realms: 
      - NexusAuthenticatingRealm
      - NexusAuthorizingRealm
      - NpmToken
      - DockerToken

setup_email:
  nexus3_email.configure:
    - enabled: True
    - host: smtp.example.com
    - port: 587
    - fromAddress: test@example.com
    - startTlsEnabled: True

# states based on pillar data
{% for blobstore, data in nexus['blobstores'].items() %}
create_blobstore_{{ blobstore }}:
  nexus3_blobstores.present:
    - name: {{ blobstore }}
  {% for item in data %}
    - {{ item }}
  {% endfor %}
{% endfor %}

remove_unwanted-blobstore:
  nexus3_blobstores.absent:
    - name: unwanted-blobstore

{% for privilege, data in nexus['privileges'].items() %}
create_privilege_{{ privilege }}:
  nexus3_privileges.present:
    - name: {{ privilege }}
  {% for item in data %}
    - {{ item }}
  {% endfor %}
{% endfor %}

remove_unwanted-privilege:
  nexus3_privileges.absent:
    - name: unwanted-privilege

{% for repository, data in nexus['repositories'].items() %}
repositories_{{ repository }}:
  nexus3_repositories.present:
    - name: {{ repository }}
  {% for item in data %}
    - {{ item }}
  {% endfor %}
{% endfor %}

remove_hosted-unwanted_repo:
  nexus3_repositories.absent:
    - name: hosted-unwanted

{% for role, data in nexus['roles'].items() %}
role_{{ role }}:
  nexus3_roles.present:
    - name: {{ role }}
  {% for item in data %}
    - {{ item }}
  {% endfor %}
{% endfor %}

remove_unwanted-role:
  nexus3_roles.absent:
    - name: unwanted-role

{% for user, data in nexus['users'].items() %}
user_{{ user }}:
  nexus3_users.present:
    - name: {{ user }}
  {% for item in data %}
    - {{ item }}
  {% endfor %}
{% endfor %}

remove_unwanted_user:
  nexus3_users.absent:
    - name: unwanted-user

# nexus3_scripts require the groovy script api to be enabled
http://localhost:8081:
  nexus3_scripts.base_url

# create tasks based on dictionary from pillars
{% for task, data in nexus['tasks'].items() %}
task_{{ task }}:
  nexus3_scripts.task:
    - name: {{ task }}
    - typeId: {{ data['typeId'] }}
    - taskProperties: {{ data['taskProperties'] }}
    - cron: {{ data['cron'] }}
  {% if data['setAlertEmail'] is defined %}
    - setAlertEmail: {{ data['setAlertEmail'] }}
  {%endif %}
{% endfor %} 
