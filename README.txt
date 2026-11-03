# Survivor Don Student Management System

A beginner-friendly Flask website with:
- Public student registration form
- Duplicate Student ID prevention
- Registration confirmation page
- Admin login
- Search by student name, course, or ID
- CSV export for Excel
- SQLite for local testing and PostgreSQL support through `DATABASE_URL`

## 1. Install Python
Install Python 3.11 or newer from https://www.python.org/downloads/ if it is not already installed.
On Windows, tick **Add Python to PATH** during installation.

## 2. Open the project folder
Extract the ZIP file to a folder such as `C:\Users\YourName\Documents\survivor_don_portal`.

In File Explorer, open that folder, click the address bar, type `cmd`, and press Enter.

## 3. Create a virtual environment and install packages
Run these commands one at a time:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Set local admin credentials
In the same Command Prompt, run these commands (replace the example password with a strong private password):

```bat
set ADMIN_USERNAME=survivordon
set ADMIN_PASSWORD=Replace-With-A-Strong-Private-Password
set SECRET_KEY=replace-with-a-long-random-secret
```

Keep your admin password private. Do not send it to students or put it in public posts.

## 5. Run the website locally
```bat
py app.py
```

Open `http://127.0.0.1:5000` in your browser.
- Public registration: `http://127.0.0.1:5000/`
- Admin login: `http://127.0.0.1:5000/admin/login`

The local database is created automatically as `survivor_don.db`.

## 6. Before putting it online
Do not deploy with the default admin password or development secret key. Set secure values in the hosting service's environment-variable settings.
For online registrations that must survive restarts and deployments, configure a hosted PostgreSQL database and set `DATABASE_URL` to its connection string. Do not rely on the local SQLite file for a hosted service with an ephemeral filesystem.
Use a reputable hosting provider, restrict dashboard access to yourself, and avoid collecting information you do not need. Student ID and other personal information should be handled carefully.

## 7. Deployment overview
1. Create a GitHub account and a new **private** repository.
2. Upload the project files, excluding `.venv`, `.env`, and database files.
3. Create a hosted PostgreSQL database with a provider such as Supabase or Render Postgres, and copy its connection URL privately.
4. Create a Render **Web Service** connected to the repository.
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app`
7. Add environment variables in the hosting dashboard:
   - `SECRET_KEY` = a long random secret
   - `ADMIN_USERNAME` = your chosen admin username
   - `ADMIN_PASSWORD` = a strong unique password
   - `DATABASE_URL` = hosted PostgreSQL connection URL
8. Deploy, then open the public `onrender.com` URL shown by Render.

Hosting free-tier terms and database retention limits can change. Check the provider's current plan and backup/retention rules before using it for real student records.
