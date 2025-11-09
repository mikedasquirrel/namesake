# PythonAnywhere Update Commands

## 🚀 Deploy Latest Changes to PythonAnywhere

After pushing to GitHub, run these commands in a **PythonAnywhere Bash console**:

### 1. Navigate to Your Web App Directory
```bash
cd ~/namesake
# or wherever your app is located, e.g.:
# cd ~/mysite
# cd ~/FlaskProject
```

### 2. Pull Latest Changes from GitHub
```bash
git pull origin main
```

### 3. Update Dependencies (if requirements.txt changed)
```bash
pip install --user -r requirements.txt
```

### 4. Reload Web App
**Option A - Via Web Tab:**
- Go to the "Web" tab in PythonAnywhere dashboard
- Click the green "Reload" button for your web app

**Option B - Via Command Line:**
```bash
# Replace 'yourusername' with your actual PythonAnywhere username
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

---

## 🔧 Complete Deployment Checklist

```bash
# Full deployment script (run in PythonAnywhere Bash):

cd ~/namesake

# Pull latest code
git pull origin main

# Install/update dependencies
pip install --user -r requirements.txt

# Check for any database migrations (if needed)
# python manage.py migrate  # if using migrations

# Reload the web app (via web tab or touch command)
```

---

## 📋 What Gets Updated

With this push, your PythonAnywhere site will receive:

✅ **New Statistical Infrastructure**
- Universal statistical suite
- Formula optimizer
- Meta-analyzer

✅ **13 Complete Findings Documents**
- Publication-ready analysis for all domains

✅ **Updated The Discoverer Page**
- Meta-analysis section with universal constant (1.344)
- Cross-domain evidence table

✅ **Master Documentation**
- Cross-domain meta-analysis
- Statistical rigor documentation
- Implementation summaries

✅ **Cleaned Documentation Structure**
- Organized files
- Archived legacy docs

---

## ⚠️ Troubleshooting

**If git pull shows conflicts:**
```bash
# Stash any local changes
git stash

# Pull fresh
git pull origin main

# Reapply your changes if needed
git stash pop
```

**If pip install fails:**
```bash
# Try upgrading pip first
pip install --user --upgrade pip

# Then install requirements
pip install --user -r requirements.txt
```

**If database.db is locked:**
```bash
# Stop any running processes
# Then reload via web tab
```

**Check error logs:**
- Go to Web tab → Log files → Error log
- Look for Python exceptions

---

## 🎯 Verify Deployment

After reloading, visit these URLs to confirm:

1. **Homepage:** `https://yourusername.pythonanywhere.com/`
2. **The Discoverer (Updated):** `https://yourusername.pythonanywhere.com/the-discoverer`
   - Should show new Section 11: "The Universal Constants: Cross-Domain Meta-Analysis"
   - Should display the constant 1.344 with full evidence table

3. **Check that all pages load:**
   - `/nba`
   - `/nfl`
   - `/mlb`
   - `/bands`
   - `/crypto`
   - etc.

---

## 💡 Quick Deploy (One-Liner)

```bash
cd ~/namesake && git pull origin main && pip install --user -r requirements.txt && echo "✅ Code updated! Now reload via Web tab"
```

Then manually click "Reload" in the Web tab.

---

**Your statistical rigor upgrade is ready to go live!** 🚀

The universal constant (1.344) will be publicly visible on The Discoverer page.

