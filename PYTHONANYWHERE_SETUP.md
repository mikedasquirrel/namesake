# PythonAnywhere Deployment Guide

## Flask Nominative Determinism Research Platform

This guide will help you deploy the Flask application to PythonAnywhere.

---

## Prerequisites

- PythonAnywhere account (Free or Paid)
- Git repository with this code
- Basic understanding of Flask applications

---

## Step 1: Clone Repository

1. Log into PythonAnywhere
2. Open a Bash console
3. Clone your repository:

```bash
cd ~
git clone https://github.com/mikedasquirrel/namesake.git FlaskProject
cd FlaskProject
```

Note: We clone as "FlaskProject" locally but the GitHub repo is "namesake"

---

## Step 2: Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.10 flask-project
pip install -r requirements.txt
```

---

## Step 3: Configure Web App

1. Go to the **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration** (not Flask wizard)
4. Select **Python 3.10**

---

## Step 4: Set WSGI Configuration

1. On the Web tab, find **Code** section
2. Set **Source code**: `/home/yourusername/FlaskProject`
3. Set **Working directory**: `/home/yourusername/FlaskProject`
4. Click on **WSGI configuration file** link
5. Replace the entire file content with a link to your wsgi.py:

```python
import sys
path = '/home/yourusername/FlaskProject'
if path not in sys.path:
    sys.path.insert(0, path)

from wsgi import application
```

Or simply link directly:
```python
import sys
sys.path.insert(0, '/home/yourusername/FlaskProject')
from wsgi import application
```

---

## Step 5: Configure Virtualenv

1. In the Web tab, find **Virtualenv** section
2. Enter path: `/home/yourusername/.virtualenvs/flask-project`
3. Click the checkmark to save

---

## Step 6: Initialize Database

Back in Bash console:

```bash
cd ~/FlaskProject
workon flask-project
export FLASK_APP=app.py
flask db upgrade
```

Or if migrations don't exist:
```bash
python
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

---

## Step 7: Set Environment Variables (Optional)

On the Web tab, scroll to **Environment variables** section and add:

- `FLASK_ENV`: `production`
- `SECRET_KEY`: `your-secret-key-here`
- `DATABASE_URL`: (if using external database)

---

## Step 8: Configure Static Files

In the Web tab, **Static files** section:

- URL: `/static/`
- Directory: `/home/yourusername/FlaskProject/static`

---

## Step 9: Reload Web App

1. Scroll to top of Web tab
2. Click **Reload yourusername.pythonanywhere.com**
3. Wait for reload to complete
4. Visit your site!

---

## Common Issues & Solutions

### Issue: ImportError

**Solution**: Make sure virtualenv is configured and all packages are installed:
```bash
workon flask-project
pip install -r requirements.txt
```

### Issue: Database not found

**Solution**: Initialize the database:
```bash
cd ~/FlaskProject
workon flask-project
python
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
```

### Issue: 500 Internal Server Error

**Solution**: Check error logs:
1. Go to Web tab
2. Click on error log link
3. Read the last few lines for the actual error

### Issue: Static files not loading

**Solution**: 
1. Check static files configuration on Web tab
2. Make sure directory path is absolute: `/home/yourusername/FlaskProject/static`
3. Reload web app

### Issue: Database is locked

**Solution**: PythonAnywhere uses a network filesystem. For SQLite:
```bash
cd ~/FlaskProject
rm -f instance/app.db*
flask db upgrade
```

For production, consider using MySQL from PythonAnywhere dashboard.

---

## Using MySQL (Recommended for Production)

1. On the **Databases** tab, create a MySQL database
2. Note the connection details
3. Update `core/config.py` with MySQL URL:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@username.mysql.pythonanywhere-services.com/username$dbname'
```

4. Install MySQL adapter:
```bash
pip install pymysql
```

5. Initialize database:
```bash
flask db upgrade
```

---

## Updating Your App

To pull updates from git:

```bash
cd ~/FlaskProject
git pull
pip install -r requirements.txt  # if requirements changed
# Reload web app from Web tab
```

---

## Performance Tips

1. **Enable GZIP compression**: PythonAnywhere does this automatically
2. **Use caching**: The app has in-memory caching built-in
3. **Optimize queries**: Use eager loading for relationships
4. **Use CDN for static files**: Consider using a CDN for production

---

## Monitoring & Logs

- **Access logs**: Web tab → Access log
- **Error logs**: Web tab → Error log  
- **Server logs**: Web tab → Server log

---

## Security Checklist

- ✅ Set `FLASK_ENV=production`
- ✅ Set strong `SECRET_KEY`
- ✅ Don't commit secrets to git
- ✅ Use environment variables for sensitive data
- ✅ Enable HTTPS (PythonAnywhere provides this)
- ✅ Keep dependencies updated

---

## Getting Help

- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- PythonAnywhere Help: https://help.pythonanywhere.com/
- Flask Documentation: https://flask.palletsprojects.com/

---

## Your App URL

After deployment, your app will be available at:
- Free accounts: `https://yourusername.pythonanywhere.com`
- Paid accounts: Can use custom domain

---

**Last Updated**: 2025-11-09
**Flask Version**: 3.0+
**Python Version**: 3.10+

