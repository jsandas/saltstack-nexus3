{% from tpldir + "/map.jinja" import nexus with context %}

# create nexus user on host that
# matches the user in the docker container
nexus_user:
  group.present:
    - name: nexus
    - gid: {{ nexus['user_id'] }}
  user.present:
    - name: nexus
    - uid: {{ nexus['user_id'] }}
    - gid: {{ nexus['user_id'] }}
    - shell: /bin/bash
    - system: True

# create folder on host to persist data
nexus_data_dir:
  file.directory:
    - name: {{ nexus['data_dir'] }}
    - user: {{ nexus['user_id'] }}
    - group: {{ nexus['user_id'] }}
    - makedirs: True
    - mode: 755

# always pull new image
nexus:
  docker_image.present:
    - force: True
    - name: sonatype/nexus3:latest
  docker_container.running:
    - name: nexus
    - image: sonatype/nexus3:latest
    - log_driver: json-file
    - log_opt:
      - max-size: "10m"
      - max-file: "3"
    - port_bindings:
      - "8081:8081"
      - "5000:5000"
    - binds:
      - {{ nexus['data_dir'] }}:/nexus-data
    - restart_policy: always
