Instructions to deploy **Minikube** with MySQL Cluster with replication and a deployment recording Client IP in the database

Install Docker CE on Ubuntu 24.04
  1. Uninstall old versions (if any):
     ```
     sudo apt remove docker docker-engine docker.io containerd runc
     ```

  2. Set up Docker’s official repository:
     ```
      sudo apt update
      sudo apt install -y ca-certificates curl gnupg
  
      # Add Docker’s GPG key:
      sudo install -m 0755 -d /etc/apt/keyrings
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
      sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
      sudo chmod a+r /etc/apt/keyrings/docker.gpg
  
      # Add the Docker apt repository:
      echo \
      "deb [arch=$(dpkg --print-architecture) \
      signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
     ```

3. Install Docker Engine:
   ```
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```

4. Start and enable Docker:
   ```
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

5. Run Docker as a non-root user:
   ```
   sudo usermod -aG docker $USER
   ```
