"""Tests for the TaskFlow web application."""

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    database_path = tmp_path / "test_tasks.sqlite3"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE": str(database_path),
        }
    )
    with app.test_client() as test_client:
        yield test_client
def add_task(client, title="Prepare report", description="Summarize weekly results"):
    return client.post(
        "/add",
        data={"title": title, "description": description},
        follow_redirects=True,
    )


def test_homepage_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"TaskFlow" in response.data
    assert b"Your day, in flow." in response.data


def test_add_task(client):
    response = add_task(client)

    assert response.status_code == 200
    assert b"Prepare report" in response.data
    assert b"Task added successfully." in response.data


def test_view_tasks_and_statistics(client):
    add_task(client)

    response = client.get("/")

    assert response.status_code == 200
    assert b"Prepare report" in response.data
    assert b'id="total-count">1</strong>' in response.data
    assert b'id="completed-count">0</strong>' in response.data
    assert b'id="pending-count">1</strong>' in response.data


def test_edit_task(client):
    add_task(client)
    response = client.post(
        "/edit/1",
        data={"title": "Updated report", "description": "Include the monthly summary"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Updated report" in response.data
    assert b"Task updated successfully." in response.data


def test_delete_task(client):
    add_task(client)
    response = client.post("/delete/1", follow_redirects=True)

    assert response.status_code == 200
    assert b"Prepare report" not in response.data
    assert b"Task deleted successfully." in response.data


def test_task_status_can_be_completed_and_pending(client):
    add_task(client)

    completed_response = client.post("/complete/1", follow_redirects=True)
    assert b"Task marked as completed." in completed_response.data
    assert b"Mark as pending" in completed_response.data

    pending_response = client.post("/complete/1", follow_redirects=True)
    assert b"Task marked as pending." in pending_response.data
    assert b"Mark as completed" in pending_response.data


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


@pytest.mark.parametrize(
    ("title", "description", "expected_message"),
    [
        ("", "Description without a title", "A task title is required."),
        ("   ", "Whitespace-only title", "A task title is required."),
        (
            "x" * 121,
            "Title exceeds the configured limit",
            "Task titles must be 120 characters or fewer.",
        ),
        (
            "Valid title",
            "x" * 2001,
            "Task descriptions must be 2000 characters or fewer.",
        ),
    ],
)
def test_invalid_task_submission_is_rejected(client, title, description, expected_message):
    response = client.post(
        "/add",
        data={"title": title, "description": description},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert expected_message.encode() in response.data
    assert b"Task added successfully." not in response.data
    assert b"No tasks yet" in response.data


def test_task_filter_shows_matching_status_only(client):
    add_task(client, title="Pending task")
    add_task(client, title="Completed task")
    client.post("/complete/2")

    response = client.get("/?status=pending")

    assert b"Pending task" in response.data
    assert b"Completed task" not in response.data


def test_missing_task_returns_not_found(client):
    assert client.get("/edit/999").status_code == 404
    assert client.post("/delete/999").status_code == 404
