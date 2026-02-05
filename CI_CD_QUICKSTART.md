# 🚀 GitHub Actions CI/CD Pipeline - Quick Start

Your repository now has a complete automated CI/CD pipeline! Here's what you need to do:

## ⚡ Quick Setup (5 minutes)

### 1. Generate SSH Key
```powershell
ssh-keygen -t rsa -b 4096 -C "github-actions" -f github-actions-key -N ""
```

### 2. Add to EC2
```bash
# On EC2 server
cat github-actions-key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. Add GitHub Secrets
Go to: **Your Repo → Settings → Secrets and variables → Actions**

Add these 4 secrets:
- `EC2_HOST` = `3.235.243.73`
- `EC2_USER` = `ubuntu`
- `EC2_PORT` = `22`
- `EC2_SSH_KEY` = (paste entire private key file content)

### 4. Done! 🎉

## 📋 What Happens Now

**Every push to `main`:**
```
Code Push → GitHub Tests → Code Quality Checks → Deploy to EC2
   ↓           (5 min)      (2 min)              (3 min)
   └─ Automatic!
```

**Every Pull Request:**
- ✅ Runs tests
- ✅ Checks code quality
- ✅ Prevents merge if tests fail

**On Main Branch (Successful Push):**
- 🚀 Auto-deploys to EC2
- 📦 Installs dependencies
- 🗄️ Runs migrations
- ♻️ Restarts services

## 📊 Monitor Your Pipeline

1. **GitHub Actions Dashboard**
   - Go to: Repo → Actions tab
   - See all workflow runs
   - Click any run to see detailed logs

2. **EC2 Services**
   ```bash
   sudo systemctl status gunicorn
   sudo systemctl status nginx
   ```

3. **Recent Deployments**
   ```bash
   cd /var/www/newshub/abdnews
   git log --oneline -5
   ```

## 🧪 Test Locally

Before pushing, test your changes:

```bash
# Install test dependencies
pip install pytest pytest-django pytest-cov coverage

# Run all tests
cd backend
pytest

# Check coverage
coverage report
```

## 📝 Commit Best Practices

```bash
# Good commit message
git commit -m "Feature: Add category filtering to article list"

# Skip deployment (if you don't want to deploy yet)
git commit -m "WIP: Update article model [skip-deploy]"

# Revert a deployment
git revert HEAD
git push
```

## 🔍 Understanding the Pipeline

### Workflow File
`.github/workflows/ci-cd.yml` - Main pipeline configuration

### What Gets Tested
- ✅ All Django unit tests
- ✅ Python code quality (flake8, black, isort)
- ✅ Database migrations
- ✅ Static file collection

### What Gets Deployed
- ✅ Latest code from main branch
- ✅ Python dependencies (from requirements.txt)
- ✅ Database migrations
- ✅ Static files
- ✅ Gunicorn & Nginx restart

## ⚠️ Common Issues

**"Permission denied (publickey)"**
- SSH key not added to EC2 `authorized_keys`
- Wrong SSH key content in GitHub secret

**"Tests passed but deployment failed"**
- Check EC2 disk space: `df -h`
- Check service logs: `sudo journalctl -u gunicorn -n 50`

**"My local tests pass but CI fails"**
- Python version mismatch (CI uses 3.12)
- PostgreSQL config different
- Missing environment variables

## 📚 Full Documentation

See `CI_CD_SETUP.md` for:
- Detailed setup instructions
- Customization options
- Security best practices
- Troubleshooting guide

## 🎯 Next Steps

1. ✅ Set up GitHub secrets (see Quick Setup above)
2. ✅ Push a test commit to main
3. ✅ Watch Actions tab for workflow run
4. ✅ Verify deployment on EC2
5. ✅ Start developing with confidence!

## 🚨 Before Production

- [ ] Test full deployment cycle
- [ ] Verify rollback procedure
- [ ] Set up monitoring/alerts
- [ ] Document deployment process
- [ ] Train team on CI/CD flow

## 💡 Pro Tips

1. **Check workflow status before pushing:**
   ```bash
   git push --force-with-lease
   ```

2. **View all recent runs:**
   - GitHub: Actions → All workflows

3. **Re-run failed deployment:**
   - GitHub: Actions → Click run → Re-run jobs

4. **Test without deploying:**
   - Add `[skip-deploy]` to commit message

5. **Debug mode:**
   - Run tests locally first: `pytest`
   - Check logs: `git log --oneline`

---

**Questions?** Check `CI_CD_SETUP.md` for detailed documentation!
