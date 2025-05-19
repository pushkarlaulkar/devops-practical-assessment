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

Install **Minikube**
```
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```


Install **kubectl** (Kubernetes CLI)

    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

Install **helm**

    curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
    chmod 700 get_helm.sh
    ./get_helm.sh

Start minikube with 2 nodes ( one control plane & one worker )
```
minikube start --driver=docker --nodes=2
```

Verify if cluster is running, also check system pods
```
kubectl get no
kubectl get po -A
```

Deploy MySQL Cluster through Helm installation ( 1 primary, 2 secondary ) in db namespace. Set root password & replication password of your choice
```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install mysql-cluster bitnami/mysql \
--namespace db \
--create-namespace \
--set architecture=replication \
--set auth.rootPassword= \
--set auth.replicationPassword= \
--set primary.persistence.enabled=true \
--set primary.persistence.size=1Gi \
--set secondary.replicaCount=2 \
--set secondary.persistence.enabled=true \
--set secondary.persistence.size=1Gi \
--set volumePermissions.enabled=true    #To fix file system permissions automatically ( without this you might error similar to mkdir: cannot create directory '/bitnami/mysql/data': Permission denied )
```

Minikube uses hostPath volumes by default for standard storage class, and sometimes the default permissions don't match the container's UID.

Create the Table in MySQL which will store the Client IP
```
kubectl exec -it -n db mysql-cluster-primary-0 -- bash
mysql -uroot -p ( Enter root user password when prompted )

CREATE DATABASE IF NOT EXISTS flaskdb;
USE flaskdb;

CREATE TABLE IF NOT EXISTS client_ips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45)
);
```

Deploy the application by running below command
```
kubectl -n web apply -f k8s-manifests/
```

This will deploy the Deployment, Secret, ConfigMap & NodePort Service

Test the API by running below command
```
curl -X POST http://public_ip:node_port/log-ip
```

This will log the IP in the database and display a json response as below
```
{
  "Client IP": "192.168.49.2", #Here minikube IP is logged
  "Time": "19 May 2025 12:27 PM"
}
```

To test database replication, first check the primary db
```
ubuntu@ip-172-31-93-224:~/devops-practical-assessment/k8s-manifests$ kubectl exec -it -n db mysql-cluster-primary-0 -- bash
Defaulted container "mysql" out of: mysql, preserve-logs-symlinks (init), volume-permissions (init)
I have no name!@mysql-cluster-primary-0:/$ mysql -uroot -p 
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 194
Server version: 9.3.0 Source distribution

Copyright (c) 2000, 2025, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> use flaskdb;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> show tables;
+-------------------+
| Tables_in_flaskdb |
+-------------------+
| client_ips        |
+-------------------+
1 row in set (0.002 sec)

mysql> select * from client_ips;
+----+--------------+
| id | ip_address   |
+----+--------------+
|  1 | 192.168.49.2 |
+----+--------------+
1 row in set (0.001 sec)
```

Next check the same for replication pod as below
```
ubuntu@ip-172-31-93-224:~/devops-practical-assessment$ kubectl exec -it -n db mysql-cluster-secondary-0 -- bash
Defaulted container "mysql" out of: mysql, preserve-logs-symlinks (init), volume-permissions (init)
I have no name!@mysql-cluster-secondary-0:/$ mysql -uroot -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 549
Server version: 9.3.0 Source distribution

Copyright (c) 2000, 2025, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> use flaskdb;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> show tables;
+-------------------+
| Tables_in_flaskdb |
+-------------------+
| client_ips        |
+-------------------+
1 row in set (0.002 sec)

mysql> select * from client_ips;
+----+--------------+
| id | ip_address   |
+----+--------------+
|  1 | 192.168.49.2 |
+----+--------------+
1 row in set (0.000 sec)
```
