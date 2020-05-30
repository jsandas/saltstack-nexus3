{% from "nexus/map.jinja" import nexus with context %}

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

nexus_data_dir:
  file.directory:
    - name: {{ nexus['data_dir'] }}
    - user: {{ nexus['user_id'] }}
    - group: {{ nexus['user_id'] }}
    - makedirs: True
    - mode: 755

nexus-image:
  docker_image.present:
    - force: True  # Ensures a new image is always pulled if the current one is out of date
    - name: sonatype/nexus3:3.18.0
nexus:
  docker_container.running:
    - name: nexus
    - image: "sonatype/nexus3:3.18.0"
    - log_driver: json-file
    - log_opt:
      - max-size: "10m"
      - max-file: "3"
    - port_bindings:
      - "8081:8081"
      - "5000:5000" # using different port than nginx is binding to
    - binds:
      - {{ nexus['data_dir'] }}:/nexus-data
    - restart_policy: always
