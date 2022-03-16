#!/bin/bash
sudo yum install -y awslogs
sudo cat << EOF > /etc/awslogs/awslogs.conf
[general]
state_file = /var/lib/awslogs/agent-state

[/var/log/messages]
file = /var/log/messages
datetime_format = %b %d %H:%M:%S
initial_position = start_of_file
log_group_name = /product/api
log_stream_name = {instance_id}
EOF
sudo systemctl restart awslogsd
sudo systemctl enable awslogsd