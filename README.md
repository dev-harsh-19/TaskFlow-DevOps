# TaskFlow

TaskFlow is a beginner-friendly task management app built with Python, Flask, and SQLite. It supports creating, viewing, editing, deleting, filtering, and completing tasks. The application and its tests run locally without AWS.

## Requirements

- Python 3.9 or newer
- pip

## Set up on Windows (PowerShell / VS Code)

Open the project folder in VS Code, then run these commands in the integrated terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, allow scripts for the current terminal session and activate again:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

## Run the application

```powershell
python app.py
```

Open <http://127.0.0.1:5000> in your browser. The SQLite database and `tasks` table are created automatically in the `instance` folder.

To use a different database path, set `TASKFLOW_DATABASE` before launching:

```powershell
$env:TASKFLOW_DATABASE = ".\instance\local-tasks.sqlite3"
python app.py
```

For development, Flask can also run the app with its reloader:

```powershell
flask --app app run --debug
```

The built-in Flask server is for local development. Use a production WSGI server and set a secure `SECRET_KEY` through the environment when preparing a production deployment.

## Run tests

```powershell
python -m pytest -v
```

Tests create an isolated SQLite database in pytest's temporary directory and do not read or modify the application's local database.

## Expected output

- The dashboard opens at `http://127.0.0.1:5000` with task statistics, filters, and an add-task form.
- New tasks start as **Pending**. Use **Mark as completed** to complete a task; the same control can return it to pending.
- Add, edit, and delete actions display a confirmation notification.
- `GET /health` returns `{"status": "healthy"}` with HTTP 200 when the database is available.
- Pytest reports all tests passing.

## Project layout

```text
TaskFlow/
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── test_app.py
├── templates/
│   ├── base.html
│   ├── edit.html
│   └── index.html
└── static/
    ├── css/style.css
    └── js/script.js
```
