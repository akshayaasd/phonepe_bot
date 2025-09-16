
#!/bin/bash

# Define variables for image and container names
docker_image_name="lt_finance_cont"
docker_container_name="lt_finance_cont"
docker_container_port=2988

# Create image
docker build -t "$docker_image_name" .

# Stop and remove the existing container
docker stop "$docker_container_name"
docker rm "$docker_container_name"

# Run the new container
docker run -d --name "$docker_container_name" -v /home/ubuntu/nlp/mount_models/:/models/ --restart unless-stopped -p $docker_container_port:8000 "$docker_image_name:latest"
