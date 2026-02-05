# CI/CD Pipeline Setup Guide

## GitHub Actions CI/CD Pipeline

This project uses GitHub Actions to automatically test, lint, and deploy code to your EC2 instance.

### What the Pipeline Does

1. **On Every Push/PR to main or develop:**
   - ✅ Runs Django unit tests
   - ✅ Generates code coverage reports
   - ✅ Checks code quality (flake8, black, isort)
   - ✅ Uploads coverage to CodeCov

2. **On Successful Push to main:**
   - 🚀 Deploys to EC2 automatically
   - 🔄 Pulls latest code
   - 📦 Installs dependencies
   - 🗄️ Runs database migrations
   - 📂 Collects static files
   - ♻️ Restarts Gunicorn & Nginx

## Setup Instructions

### Step 1: Generate SSH Key Pair

On your local machine (Windows PowerShell):

```powershell
# Generate SSH key
ssh-keygen -t rsa -b 4096 -C "github-actions" -f github-actions-key -N ""

# View the private key (you'll need this)
cat github-actions-key

# View the public key
cat github-actions-key.pub
```

### Step 2: Add Public Key to EC2

On your EC2 server:

```bash
# Add the public key to authorized_keys
echo "your-public-key-content-here" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Verify
cat ~/.ssh/authorized_keys
```

### Step 3: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Click "New repository secret" and add these secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `EC2_HOST` | Your EC2 public IP | `3.235.243.73` |
| `EC2_USER` | EC2 username | `ubuntu` |
| `EC2_PORT` | SSH port | `22` |
| `EC2_SSH_KEY` | Private SSH key contents | (paste entire private key) |

**Important:** For `EC2_SSH_KEY`, copy the ENTIRE contents of your private key file, including:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
...
-----END RSA PRIVATE KEY-----
```

### Step 4: Verify Setup

1. Go to your GitHub repo → Actions
2. Push a test commit to main branch
3. Watch the workflow run
4. Check the logs for any issues

## Workflow File Location

The CI/CD workflow is defined in:
```
.github/workflows/ci-cd.yml
```

## Understanding the Workflow

### Test Job
- Spins up PostgreSQL test database
- Runs Django migrations on test DB
- Executes all unit tests
- Generates coverage reports
- Uploads to CodeCov (optional)

### Lint Job
- Checks Python syntax with flake8
- Validates code format with black
- Checks import ordering with isort
- Runs in "continue-on-error" mode (won't block deployment)

### Deploy Job
- Only runs on successful main branch push
- SSH into EC2
- Pulls latest code
- Installs Python dependencies
- Runs migrations
- Collects static files
- Restarts application services

## Customization

### Environment Variables for Tests

Edit `.github/workflows/ci-cd.yml` to change test database settings:

```yaml
env:
  DATABASE_NAME: test_newshub_db
  DATABASE_USER: postgres
  DATABASE_PASSWORD: postgres
```

### Disable Deployment for Specific Commits

Add `[skip-deploy]` to your commit message:

```bash
git commit -m "Fix: Minor bug fix [skip-deploy]"
```

Then modify the deploy job condition in the workflow.

### Slack Notifications (Optional)

Add to notify your team:

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

Then add `SLACK_WEBHOOK` secret with your Slack webhook URL.

## Troubleshooting

### "Permission denied (publickey)" Error

1. Verify SSH key was added to EC2: `cat ~/.ssh/authorized_keys`
2. Check key format - should have `-----BEGIN RSA PRIVATE KEY-----`
3. Ensure EC2 security group allows port 22 inbound

### Tests Failing Locally but Passing in CI

1. Check Python version: CI uses Python 3.12
2. Ensure PostgreSQL is running locally
3. Set same environment variables as CI

### Deployment Not Running

1. Confirm you're pushing to `main` branch
2. Check that test and lint jobs passed
3. Verify EC2 secrets are set correctly

## View Logs

1. GitHub: Go to Actions tab → Click workflow run → View logs
2. EC2: Check deployment logs in `/var/log/syslog`

```bash
sudo tail -f /var/log/syslog | grep gunicorn
sudo tail -f /var/log/nginx/error.log
```

## Security Best Practices

1. ✅ Use long, complex SSH keys
2. ✅ Rotate SSH keys periodically
3. ✅ Never commit secrets to repository
4. ✅ Use GitHub Secrets for sensitive data
5. ✅ Limit SSH key permissions (chmod 600)
6. ✅ Monitor deployment logs regularly
7. ✅ Use separate deploy key from personal SSH keys

## Next Steps

1. Test the pipeline with a dummy commit
2. Monitor the first deployment
3. Check EC2 services after deployment
4. Update workflow based on your needs
5. Consider adding email/Slack notifications

## Support

For issues with the CI/CD pipeline:
1. Check GitHub Actions logs
2. SSH into EC2 and check service status
3. Review error messages in workflow output
