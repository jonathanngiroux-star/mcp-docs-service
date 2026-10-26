#!/usr/bin/env python3
"""
MCP Docs Service Server - Technical Documentation (FR/EN) via MCP
"""

import json
import asyncio
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from mcp.server import Server
from mcp.types import Tool, TextContent, ListToolsResult, CallToolResult

DB_PATH = Path(__file__).parent / "docs.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                default_language TEXT NOT NULL,
                supported_languages TEXT NOT NULL,
                repo_url TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                language TEXT NOT NULL,
                version TEXT NOT NULL,
                format TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)

init_db()

TOOLS = [
    Tool(
        name="write_api_docs",
        description="Write API documentation for a project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID"},
                "title": {"type": "string", "description": "Document title"},
                "content": {"type": "string", "description": "Document content in markdown"},
                "language": {"type": "string", "enum": ["en", "fr"], "default": "en"},
                "format": {"type": "string", "enum": ["markdown", "rst"], "default": "markdown"}
            },
            "required": ["project_id", "title", "content"]
        }
    ),
    Tool(
        name="write_integration_guide",
        description="Write integration guide for a project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID"},
                "title": {"type": "string", "description": "Guide title"},
                "content": {"type": "string", "description": "Guide content in markdown"},
                "language": {"type": "string", "enum": ["en", "fr"], "default": "en"}
            },
            "required": ["project_id", "title", "content"]
        }
    ),
    Tool(
        name="translate_docs",
        description="Translate document to another language",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "Document ID to translate"},
                "target_language": {"type": "string", "enum": ["en", "fr"], "description": "Target language"}
            },
            "required": ["doc_id", "target_language"]
        }
    ),
    Tool(
        name="lint_docs",
        description="Check documentation for issues",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID"},
                "language": {"type": "string", "enum": ["en", "fr"], "default": "en"}
            },
            "required": ["project_id"]
        }
    ),
    Tool(
        name="create_project",
        description="Create a new documentation project",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Project name"},
                "description": {"type": "string", "description": "Project description"},
                "default_language": {"type": "string", "enum": ["en", "fr"], "default": "en"},
                "supported_languages": {"type": "array", "items": {"type": "string", "enum": ["en", "fr"]}, "default": ["en", "fr"]},
                "repo_url": {"type": "string", "description": "Repository URL (optional)"}
            },
            "required": ["name"]
        }
    ),
    Tool(
        name="list_documents",
        description="List documents for a project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID"},
                "language": {"type": "string", "enum": ["en", "fr"]}
            },
            "required": ["project_id"]
        }
    )
]

async def list_tools_handler():
    from mcp.types import ListToolsResult
    return ListToolsResult(tools=TOOLS)

async def call_tool_handler(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    try:
        if name == "write_api_docs":
            result = await write_api_docs(arguments)
        elif name == "write_integration_guide":
            result = await write_integration_guide(arguments)
        elif name == "translate_docs":
            result = await translate_docs(arguments)
        elif name == "lint_docs":
            result = await lint_docs(arguments)
        elif name == "create_project":
            result = await create_project(arguments)
        elif name == "list_documents":
            result = await list_documents(arguments)
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")], isError=True)
        return CallToolResult(content=result)
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")], isError=True)

async def create_project(args: Dict[str, Any]) -> List[TextContent]:
    name = args["name"]
    description = args.get("description", "")
    default_language = args.get("default_language", "en")
    supported_languages = args.get("supported_languages", ["en", "fr"])
    repo_url = args.get("repo_url", "")
    
    project_id = f"proj-{name.lower().replace(' ', '-')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    now = datetime.now().isoformat()
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO projects (id, name, description, default_language, supported_languages, repo_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (project_id, name, description, default_language, json.dumps(supported_languages), repo_url, now))
    
    return [TextContent(type="text", text=json.dumps({
        "project_id": project_id,
        "name": name,
        "status": "created"
    }, indent=2))]

async def write_api_docs(args: Dict[str, Any]) -> List[TextContent]:
    project_id = args["project_id"]
    title = args["title"]
    content = args["content"]
    language = args.get("language", "en")
    format = args.get("format", "markdown")
    
    doc_id = f"doc-{project_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    now = datetime.now().isoformat()
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO documents (id, project_id, title, content, language, version, format, tags, created_at, updated_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, project_id, title, content, language, "1.0", format, json.dumps(["api"]), now, now, "draft"))
    
    return [TextContent(type="text", text=json.dumps({
        "doc_id": doc_id,
        "title": title,
        "language": language,
        "status": "draft"
    }, indent=2))]

async def write_integration_guide(args: Dict[str, Any]) -> List[TextContent]:
    project_id = args["project_id"]
    title = args["title"]
    content = args["content"]
    language = args.get("language", "en")
    
    doc_id = f"guide-{project_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    now = datetime.now().isoformat()
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO documents (id, project_id, title, content, language, version, format, tags, created_at, updated_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, project_id, title, content, language, "1.0", "markdown", json.dumps(["guide"]), now, now, "draft"))
    
    return [TextContent(type="text", text=json.dumps({
        "doc_id": doc_id,
        "title": title,
        "language": language,
        "status": "draft"
    }, indent=2))]

async def translate_docs(args: Dict[str, Any]) -> List[TextContent]:
    doc_id = args["doc_id"]
    target_language = args["target_language"]
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            return [TextContent(type="text", text=json.dumps({"error": "Document not found"}))]
        
        # In production, would call translation API
        translated_content = f"[{target_language.upper()}] {row['content']}"
        
        new_doc_id = f"{doc_id}-{target_language}"
        now = datetime.now().isoformat()
        
        conn.execute("""
            INSERT INTO documents (id, project_id, title, content, language, version, format, tags, created_at, updated_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_doc_id, row["project_id"], f"[{target_language.upper()}] {row['title']}", translated_content, target_language, row["version"], row["format"], row["tags"], datetime.now().isoformat(), datetime.now().isoformat(), "draft"))
    
    return [TextContent(type="text", text=json.dumps({
        "doc_id": new_doc_id,
        "original_id": doc_id,
        "language": target_language,
        "status": "translated"
    }, indent=2))]

async def lint_docs(args: Dict[str, Any]) -> List[TextContent]:
    project_id = args["project_id"]
    language = args.get("language", "en")
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM documents WHERE project_id = ? AND language = ?", (project_id, language)).fetchall()
        docs = [dict(r) for r in rows]
    
    issues = []
    for doc in docs:
        if not doc["content"] or len(doc["content"]) < 50:
            issues.append({"doc_id": doc["id"], "issue": "Content too short"})
        if "TODO" in doc["content"] or "FIXME" in doc["content"]:
            issues.append({"doc_id": doc["id"], "issue": "Contains TODO/FIXME"})
    
    return [TextContent(type="text", text=json.dumps({
        "project_id": project_id,
        "language": language,
        "total_docs": len(docs),
        "issues": issues,
        "status": "pass" if not issues else "issues_found"
    }, indent=2))]

async def list_documents(args: Dict[str, Any]) -> List[TextContent]:
    project_id = args["project_id"]
    language = args.get("language")
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        if language:
            rows = conn.execute("SELECT * FROM documents WHERE project_id = ? AND language = ?", (project_id, language)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM documents WHERE project_id = ?", (project_id,)).fetchall()
        docs = [dict(r) for r in rows]
    
    return [TextContent(type="text", text=json.dumps({
        "project_id": project_id,
        "documents": [{"id": d["id"], "title": d["title"], "language": d["language"], "status": d["status"], "updated_at": d["updated_at"]} for d in docs]
    }, indent=2))]

from mcp.types import Tool, TextContent, ListToolsResult, CallToolResult

init_db()

TOOLS = [
    Tool(
        name="create_project",
        description="Create a new documentation project",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Project name"},
                "description": {"type": "string", "description": "Project description"},
                "default_language": {"type": "string", "enum": ["en", "fr"], "default": "en"},
                "supported_languages": {"type": "array", "items": {"type": "string", "enum": ["en", "fr"]}, "default": ["en", "fr"]},
                "repo_url": {"type": "string", "description": "Repository URL (optional)"}
            },
            "required": ["name"]
        }
    ),
    Tool(
        name="write_api_docs",
        description="Write API documentation for a project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID"},
                "title": {"type": "string", "description": "Document title"},
                "content": {"type": "string", "description": "Document content in markdown"},
                "language": {"type": "string", "enum": ["en", "fr"], "default": "en"},
                "format": {"type": "string", "enum": ["markdown", "rst"], "default": "markdown"}
            },
            "required": ["project_id", "title", "content"]
        }
    ),
    Tool(
        name="write_integration_guide",
        description="Write integration guide for a project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID"},
                "title": {"type": "string", "description": "Guide title"},
                "content": {"type": "string", "description": "Guide content in markdown"},
                "language": {"type": "string", "enum": ["en", "fr"], "default": "en"}
            },
            "required": ["project_id", "title", "content"]
        }
    ),
    Tool(
        name="translate_docs",
        description="Translate document to another language (EN/FR)",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "Document ID to translate"},
                "target_language": {"type": "string", "enum": ["en", "fr"], "description": "Target language"}
            },
            "required": ["doc_id", "target_language"]
        }
    ),
    Tool(
        name="lint_docs",
        description="Check documentation for issues",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID"},
                "language": {"type": "string", "enum": ["en", "fr"], "default": "en"}
            },
            "required": ["project_id"]
        }
    ),
    Tool(
        name="list_documents",
        description="List documents for a project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID"},
                "language": {"type": "string", "enum": ["en", "fr"]}
            },
            "required": ["project_id"]
        }
    )
]

async def list_tools_handler():
    from mcp.types import ListToolsResult
    return ListToolsResult(tools=TOOLS)

async def call_tool_handler(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    try:
        if name == "create_project":
            result = await create_project(arguments)
        elif name == "write_api_docs":
            result = await write_api_docs(arguments)
        elif name == "write_integration_guide":
            result = await write_integration_guide(arguments)
        elif name == "translate_docs":
            result = await translate_docs(arguments)
        elif name == "lint_docs":
            result = await lint_docs(arguments)
        elif name == "list_documents":
            result = await list_documents(arguments)
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")], isError=True)
        return CallToolResult(content=result)
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")], isError=True)

app = Server(
    name="mcp-docs-service",
    on_list_tools=lambda: list_tools_handler(),
    on_call_tool=lambda name, arguments: call_tool_handler(name, arguments)
)

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    async def serve():
        server = await stdio_server()
        await app.run(server.stdin, server.stdout)
    asyncio.run(serve())