# Django Project Deployment Guide

Deploying the project backend to Hetzner Cloud using Terraform and Ansible.

## Prerequisites

Before starting the deployment process, ensure you have:

1. **Hetzner Cloud Account**: You'll need an account with Hetzner Cloud (https://www.hetzner.com/cloud)
2. **Terraform**: Install Terraform CLI (v1.0.0+) on your local machine
3. **Ansible**: Install Ansible (v2.9+) on your local machine

## Step 1: Hetzner Cloud Setup

Before running Terraform, you need to set up a few things in your Hetzner Cloud account:

1. **Create a Project**:

    - Log in to Hetzner Cloud Console
    - Create a new project (e.g., "Project Name")

2. **Generate API Token**:

    - In your project, go to "Security" > "API Tokens"
    - Click "Generate API Token"
    - Select "Read & Write" permissions
    - Copy the token (you'll only see it once)

3. **Get S3 Credentials** (for S3 buckets):
    - Go to "Security" > "S3 Credentials"
    - Create credentials for the project
    - Note down your Access Key and Secret Key
    - (S3 credentials are project-wide, not bucket-specific)

## Step 2: Deploy Infrastructure with Terraform

1. **Create terraform.tfvars File**:

Copy `terraform/terraform.tfvars.example` to `terraform/terraform.tfvars` and update the variables. This file serves as the configuration source for your Terraform deployment.

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

2. **Initialize Terraform**:

```bash
cd terraform
terraform init
```

3. **Deploy Resources**:

```bash
terraform apply
```

4. **Note the Outputs**:

After successful deployment, Terraform will display the output variables.

If a variable is cut off, view it specifically with: `terraform output <variable_name>`

-   `server_ip`: Your server's public IP address
-   `server_status`: Status of the server
-   `hetzner_s3_access_key`: Access key for the Hetzner S3 bucket
-   `hetzner_s3_secret_key`: Secret key for the Hetzner S3 bucket
-   `hetzner_s3_bucket_name`: Name of the S3 bucket for application media files
-   `hetzner_s3_endpoint_url`: Endpoint URL for the S3 bucket for application media files (eg. https://nbg1.your-objectstorage.com)

## Step 3: Setup the domain name

Create an A record from "api." to your server's IP address.

## Step 4: SSH Key Setup

1. **Prepare SSH Keys**:

    - Get your personal SSH public key: `cat ~/.ssh/id_rsa.pub`
    - Generate a key pair for GitHub Actions:
        ```bash
        ssh-keygen -t ed25519 -C "github-actions@jobfunnel" -N "" -f /tmp/github-actions-key-$$ && \
        echo "=== PRIVATE KEY (for DOKKU_SSH_PRIVATE_KEY secret) ===" && \
        cat /tmp/github-actions-key-$$ && \
        echo -e "\n\n=== PUBLIC KEY (to add to Hetzner) ===" && \
        cat /tmp/github-actions-key-$$.pub && \
        rm -f /tmp/github-actions-key-$$ /tmp/github-actions-key-$$.pub
        ```

2. **Access the Server**:

    - You'll receive an email from Hetzner with the server's root password
    - Log in to the server: `ssh root@<server-ip>`

3. **Install SSH Keys on the Server** (for existing servers):
    - Follow the commands below to add both SSH keys

```bash
# Mount your server's root partition (usually /dev/sda1 or /dev/sda3)
mount /dev/sda1 /mnt  # or /dev/sda3

# Create SSH directory
mkdir -p /mnt/root/.ssh

# Add your personal SSH key
echo "<YOUR_PERSONAL_SSH_KEY>" > /mnt/root/.ssh/authorized_keys

# Add GitHub Actions SSH key (append to the file)
echo "<GITHUB_ACTIONS_PUBLIC_KEY>" >> /mnt/root/.ssh/authorized_keys

# Set proper permissions
chmod 600 /mnt/root/.ssh/authorized_keys
chmod 700 /mnt/root/.ssh

# Unmount
umount /mnt

# Reboot back to normal mode
reboot
```

## Step 5: Set Up Ansible for Application Deployment

After deploying the infrastructure with Terraform, you'll use Ansible to deploy the application to your server:

1. **Configure a .env.production File**:

Copy `.env.production.example` to `.env.production` and update the variables. These variables will be set for the backend application.

```bash
cp .env.production.example .env.production
```

2. **Navigate to the Ansible Directory**:

```bash
cd ansible
```

2. **Create ansible_env.yml File**:

Copy `ansible_env.yml.example` to `ansible_env.yml` and update the variables. This file serves as the configuration source for your Ansible deployment.

```bash
cp ansible_env.yml.example ansible_env.yml
```

3. **Update Inventory File**:

Manually update the `inventory/hosts` file with your server's IP address (from Terraform output):

```ini
[app_server]
app ansible_host=XXX-YOUR-SERVER-IP-XXX ansible_user=root ...
```

## Step 6: Configure Let's Encrypt

The deployment automatically sets up Let's Encrypt for HTTPS. Make sure to:

1. **Set Email for Let's Encrypt**: Add `DJANGO_SUPERUSER_EMAIL` to your `.env.production` file. This email will be used for Let's Encrypt certificate notifications.

2. **Ensure Firewall Allows HTTP**: Make sure port 80 is open in your firewall configuration to allow Let's Encrypt domain verification.

3. **DNS Configuration**: Ensure your domain's DNS records point to your server's IP address before running the Ansible playbook.

## Step 7: Deploy Application with Ansible

Now you're ready to deploy the application using Ansible:

1. **Run the Ansible Playbook**:

```bash
ansible-playbook -i inventory/hosts site.yml -v
```

## Checking Deployment Status

After deployment, you can check the status of your application:

```bash
ansible -i inventory/hosts app_server -m shell -a "dokku ps:report your-project-name-backend"
```

To view logs:

```bash
ansible -i inventory/hosts app_server -m shell -a "dokku logs your-project-name-backend -t"
```

## Step 8: Setup GitHub Actions

Add the following secrets to your GitHub repository:

-   `DOKKU_GIT_REMOTE_URL`: `ssh://dokku@$HETZNER_SERVER_IP:22/$DOKKU_APP_NAME`
    -   with DOKKU_APP_NAME = ansible_env_vars.DOKKU_APP_NAME ----> from ansible_env.yml
    -   with HETZNER_SERVER_IP = your-server-ip ----> from terraform output
-   `DOKKU_SSH_PRIVATE_KEY`: An SSH private key that has access to your Hetzner Project
    -   just like you set up your personal SSH key pair but preferably a server key

You can find these settings at https://github.com/YOUR-GITHUB-ORG/YOUR-GITHUB-REPO/settings/secrets/actions

## Troubleshooting

If you encounter issues during deployment:

1. Check the Ansible output for error messages
2. Verify that your `ansible_env.yml` file contains the correct values
3. Ensure your `.env.production` file is properly configured
4. Access the server from local machine with ssh: `ssh -i ~/.ssh/id_rsa root@your-server-ip`
