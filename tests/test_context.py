"""
Tests pour le module context
"""
import pytest
from datetime import datetime

from auto_antigravity.core.context import Context, Task, TaskStatus, AgentType


def test_task_creation():
    """Test la création d'une tâche"""
    task = Task(
        id="test_task",
        description="Description de test"
    )
    
    assert task.id == "test_task"
    assert task.description == "Description de test"
    assert task.status == TaskStatus.PENDING
    assert task.dependencies == []
    assert task.subtasks == []
    assert task.assigned_agent is None


def test_context_creation():
    """Test la création d'un contexte"""
    context = Context(
        project_path="/test/path",
        project_name="TestProject",
        project_description="A test project"
    )
    
    assert context.project_path == "/test/path"
    assert context.project_name == "TestProject"
    assert context.project_description == "A test project"
    assert context.tasks == {}
    assert context.tasks_completed == 0
    assert context.tasks_failed == 0


def test_add_message():
    """Test l'ajout d'un message"""
    context = Context(
        project_path="/test/path",
        project_name="TestProject",
        project_description="A test project"
    )
    
    context.add_message("user", "Hello", AgentType.PLANNER)
    
    assert len(context.messages) == 1
    assert context.messages[0]["role"] == "user"
    assert context.messages[0]["content"] == "Hello"
    assert context.messages[0]["agent"] == "planner"


def test_update_task_status():
    """Test la mise à jour du statut d'une tâche"""
    context = Context(
        project_path="/test/path",
        project_name="TestProject",
        project_description="A test project"
    )
    
    task = Task(id="test", description="Test task")
    context.tasks["test"] = task
    
    context.update_task_status("test", TaskStatus.COMPLETED, "Done")
    
    assert context.tasks["test"].status == TaskStatus.COMPLETED
    assert context.tasks["test"].result == "Done"
    assert context.tasks_completed == 1


def test_get_pending_tasks():
    """Test la récupération des tâches en attente"""
    context = Context(
        project_path="/test/path",
        project_name="TestProject",
        project_description="A test project"
    )
    
    task1 = Task(id="1", description="Pending task")
    task2 = Task(id="2", description="Completed task", status=TaskStatus.COMPLETED)
    
    context.tasks["1"] = task1
    context.tasks["2"] = task2
    
    pending = context.get_pending_tasks()
    
    assert len(pending) == 1
    assert pending[0].id == "1"


def test_get_tasks_for_agent():
    """Test la récupération des tâches assignées à un agent"""
    context = Context(
        project_path="/test/path",
        project_name="TestProject",
        project_description="A test project"
    )
    
    task1 = Task(
        id="1",
        description="Coder task",
        assigned_agent=AgentType.CODER,
        status=TaskStatus.PENDING
    )
    task2 = Task(
        id="2",
        description="Planner task",
        assigned_agent=AgentType.PLANNER,
        status=TaskStatus.PENDING
    )
    
    context.tasks["1"] = task1
    context.tasks["2"] = task2
    
    coder_tasks = context.get_tasks_for_agent(AgentType.CODER)
    
    assert len(coder_tasks) == 1
    assert coder_tasks[0].assigned_agent == AgentType.CODER
