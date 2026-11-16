"""Flask application for TaskFlow."""

import sqlite3
from contextlib import closing

from flask import Flask, abort, flash, redirect, render_template, request, url_for

from config import Config
from database import connect_db, init_db


def create_app(test_config=None):
    """Create and configure a TaskFlow application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    init_db(app.config["DATABASE"])

    def get_task(task_id):
        with closing(connect_db(app.config["DATABASE"])) as connection:
            task = connection.execute(
                "SELECT id, title, description, status, created_at "
                "FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        if task is None:
            abort(404)
        return task

    @app.get("/")
    def index():
        selected_status = request.args.get("status", "all")
        allowed_statuses = {"all", "pending", "completed"}
        if selected_status not in allowed_statuses:
            abort(400)

        with closing(connect_db(app.config["DATABASE"])) as connection:
            statistics = connection.execute(
                """
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
                       SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending
                FROM tasks
                """
            ).fetchone()

            if selected_status == "all":
                tasks = connection.execute(
                    "SELECT id, title, description, status, created_at "
                    "FROM tasks ORDER BY id DESC"
                ).fetchall()
            else:
                tasks = connection.execute(
                    "SELECT id, title, description, status, created_at "
                    "FROM tasks WHERE status = ? ORDER BY id DESC",
                    (selected_status,),
                ).fetchall()

        stats = {
            "total": statistics["total"],
            "completed": statistics["completed"] or 0,
            "pending": statistics["pending"] or 0,
        }
        return render_template(
            "index.html",
            tasks=tasks,
            stats=stats,
            selected_status=selected_status,
            title_max_length=app.config["TITLE_MAX_LENGTH"],
            description_max_length=app.config["DESCRIPTION_MAX_LENGTH"],
        )

    @app.post("/add")
    def add_task():
        title, description = _validated_task_form(app)
        if title is None:
            flash(description, "error")
            return redirect(url_for("index"))

        with closing(connect_db(app.config["DATABASE"])) as connection:
            connection.execute(
                "INSERT INTO tasks (title, description, status) "
                "VALUES (?, ?, 'pending')",
                (title, description),
            )
            connection.commit()

        flash("Task added successfully.", "success")
        return redirect(url_for("index"))

    @app.get("/edit/<int:task_id>")
    def edit_task(task_id):
        task = get_task(task_id)
        return render_template(
            "edit.html",
            task=task,
            title_max_length=app.config["TITLE_MAX_LENGTH"],
            description_max_length=app.config["DESCRIPTION_MAX_LENGTH"],
        )

    @app.post("/edit/<int:task_id>")
    def update_task(task_id):
        get_task(task_id)
        title, description = _validated_task_form(app)
        if title is None:
            flash(description, "error")
            return redirect(url_for("edit_task", task_id=task_id))

        with closing(connect_db(app.config["DATABASE"])) as connection:
            connection.execute(
                "UPDATE tasks SET title = ?, description = ? WHERE id = ?",
                (title, description, task_id),
            )
            connection.commit()

        flash("Task updated successfully.", "success")
        return redirect(url_for("index"))

    @app.post("/delete/<int:task_id>")
    def delete_task(task_id):
        get_task(task_id)
        with closing(connect_db(app.config["DATABASE"])) as connection:
            connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            connection.commit()

        flash("Task deleted successfully.", "success")
        return redirect(url_for("index"))

    @app.post("/complete/<int:task_id>")
    def toggle_task_status(task_id):
        task = get_task(task_id)
        new_status = "pending" if task["status"] == "completed" else "completed"
        with closing(connect_db(app.config["DATABASE"])) as connection:
            connection.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (new_status, task_id),
            )
            connection.commit()

        message = "Task marked as completed." if new_status == "completed" else "Task marked as pending."
        flash(message, "success")
        return redirect(url_for("index"))

    @app.get("/health")
    def health():
        try:
            with closing(connect_db(app.config["DATABASE"])) as connection:
                connection.execute("SELECT 1").fetchone()
        except sqlite3.Error:
            app.logger.exception("Database health check failed")
            return {"status": "unhealthy"}, 503
        return {"status": "healthy"}, 200

    return app


def _validated_task_form(app):
    """Return sanitized form data, or (None, an error message)."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not title:
        return None, "A task title is required."
    if len(title) > app.config["TITLE_MAX_LENGTH"]:
        return None, f"Task titles must be {app.config['TITLE_MAX_LENGTH']} characters or fewer."
    if len(description) > app.config["DESCRIPTION_MAX_LENGTH"]:
        return None, (
            "Task descriptions must be "
            f"{app.config['DESCRIPTION_MAX_LENGTH']} characters or fewer."
        )
    return title, description


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
