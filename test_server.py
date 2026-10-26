import pytest
import asyncio
import json
from mcp_docs_service.server import (
    create_project, 
    write_api_docs, 
    write_integration_guide,
    translate_docs,
    lint_docs,
    list_documents,
    list_tools_handler,
    call_tool_handler
)

@pytest.fixture
async def clean_db():
    import sqlite3
    from mcp_docs_service.server import DB_PATH
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM projects")
        conn.execute("DELETE FROM documents")
    yield
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM projects")
        conn.execute("DELETE FROM documents")

@pytest.mark.asyncio
async def test_list_tools():
    from mcp_docs_service.server import list_tools_handler
    from mcp.types import ListToolsResult
    result = await list_tools_handler()
    assert isinstance(result, ListToolsResult)
    assert len(result.tools) == 6
    tool_names = {t.name for t in result.tools}
    assert "create_project" in tool_names
    assert "write_api_docs" in tool_names
    assert "write_integration_guide" in tool_names
    assert "translate_docs" in tool_names
    assert "lint_docs" in tool_names
    assert "list_documents" in tool_names

@pytest.mark.asyncio
async def test_create_project(clean_db):
    from mcp_docs_service.server import create_project
    result = await create_project({
        "name": "Test Project",
        "description": "A test project",
        "default_language": "en",
        "supported_languages": ["en", "fr"],
        "repo_url": "https://github.com/test/project"
    })
    assert len(result) > 0
    data = json.loads(result[0].text)
    assert data["name"] == "Test Project"
    assert "project_id" in data

@pytest.mark.asyncio
async def test_write_api_docs(clean_db):
    from mcp_docs_service.server import create_project, write_api_docs, list_documents
    # Create project first
    proj_result = await create_project({
        "name": "Test Project",
        "description": "A test project",
        "default_language": "en",
        "supported_languages": ["en", "fr"]
    })
    project_id = json.loads(proj_result[0].text)["project_id"]
    
    # Write API docs
    result = await write_api_docs({
        "project_id": project_id,
        "title": "API Reference",
        "content": "# API Reference\n\n## GET /users\nReturns users",
        "language": "en"
    })
    assert len(result) > 0
    data = json.loads(result[0].text)
    assert "doc_id" in data
    
    # List documents
    list_result = await list_documents({"project_id": project_id})
    docs_data = json.loads(list_result[0].text)
    assert len(docs_data["documents"]) >= 1

@pytest.mark.asyncio
async def test_write_integration_guide(clean_db):
    from mcp_docs_service.server import create_project, write_integration_guide
    proj_result = await create_project({"name": "Test", "description": "Test"})
    project_id = json.loads(proj_result[0].text)["project_id"]
    
    result = await write_integration_guide({
        "project_id": project_id,
        "title": "Getting Started",
        "content": "# Getting Started\n\n1. Install\n2. Configure",
        "language": "en"
    })
    data = json.loads(result[0].text)
    assert data["status"] == "draft"

@pytest.mark.asyncio
async def test_translate_docs(clean_db):
    from mcp_docs_service.server import create_project, write_api_docs, translate_docs
    proj_result = await create_project({"name": "Test", "description": "Test"})
    project_id = json.loads(proj_result[0].text)["project_id"]
    
    doc_result = await write_api_docs({
        "project_id": project_id,
        "title": "Test Doc",
        "content": "English content",
        "language": "en"
    })
    doc_id = json.loads(doc_result[0].text)["doc_id"]
    
    # Translate to French
    result = await translate_docs({
        "doc_id": doc_id,
        "target_language": "fr"
    })
    data = json.loads(result[0].text)
    assert data["language"] == "fr"
    assert data["original_id"] == doc_id

@pytest.mark.asyncio
async def test_lint_docs(clean_db):
    from mcp_docs_service.server import create_project, write_api_docs, lint_docs
    proj_result = await create_project({"name": "Test", "description": "Test"})
    project_id = json.loads(proj_result[0].text)["project_id"]
    
    # Write a doc with issues
    await write_api_docs({
        "project_id": project_id,
        "title": "Short",
        "content": "Short",
        "language": "en"
    })
    
    result = await lint_docs({"project_id": project_id, "language": "en"})
    data = json.loads(result[0].text)
    assert data["total_docs"] >= 1
    assert len(data["issues"]) >= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])