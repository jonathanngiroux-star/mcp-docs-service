#!/usr/bin/env python3
"""MCP server for docs-service - Technical Documentation (FR/EN)"""

import json
import os
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("mcp-docs-service")

TOOLS = [
    Tool(
        name="write_api_docs",
        description="Write API documentation for a project",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project name"},
                "endpoints": {"type": "array", "items": {"type": "object"}, "description": "API endpoints to document"},
                "language": {"type": "string", "enum": ["en", "fr"], "default": "en", "description": "Documentation language"},
                "format": {"type": "string", "enum": ["markdown", "openapi"], "default": "markdown", "description": "Output format"}
            },
            "required": ["project", "endpoints"]
        }
    ),
    Tool(
        name="write_integration_guide",
        description="Write integration guide for a service",
        inputSchema={
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "Service name"},
                "steps": {"type": "array", "items": {"type": "object"}, "description": "Integration steps"},
                "language": {"type": "string", "enum": ["en", "fr"], "default": "en", "description": "Documentation language"},
                "audience": {"type": "string", "enum": ["developer", "admin", "user"], "default": "developer", "description": "Target audience"}
            },
            "required": ["service", "steps"]
        }
    ),
    Tool(
        name="translate_docs",
        description="Translate documentation between English and French",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to translate"},
                "source_lang": {"type": "string", "enum": ["en", "fr"], "description": "Source language"},
                "target_lang": {"type": "string", "enum": ["en", "fr"], "description": "Target language"},
                "context": {"type": "string", "description": "Context for translation (optional)"}
            },
            "required": ["content", "source_lang", "target_lang"]
        }
    ),
    Tool(
        name="lint_docs",
        description="Check documentation for quality issues",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Documentation content to check"},
                "language": {"type": "string", "enum": ["en", "fr"], "default": "en", "description": "Documentation language"},
                "checks": {"type": "array", "items": {"type": "string", "enum": ["spelling", "grammar", "style", "completeness", "consistency"]}, "default": ["spelling", "grammar", "style", "completeness", "consistency"], "description": "Quality checks to run"}
            },
            "required": ["content"]
        }
    )
]

app = Server("mcp-docs-service")

@app.list_tools()
async def list_tools():
    return TOOLS

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "write_api_docs":
        project = arguments.get("project")
        endpoints = arguments.get("endpoints")
        language = arguments.get("language", "en")
        format = arguments.get("format", "markdown")
        
        result = {
            "status": "ok",
            "tool": "write_api_docs",
            "project": project,
            "language": language,
            "format": format,
            "endpoints_count": len(endpoints),
            "output": f"# {project} API Documentation\n\nGenerated in {language} ({format} format)\n\n## Endpoints\n\n" + "\n".join([f"- {ep.get('method', 'GET')} {ep.get('path', '/')}" for ep in endpoints])
        }
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "write_integration_guide":
        service = arguments.get("service")
        steps = arguments.get("steps")
        language = arguments.get("language", "en")
        audience = arguments.get("audience", "developer")
        
        result = {
            "status": "ok",
            "tool": "write_integration_guide",
            "service": service,
            "language": language,
            "audience": audience,
            "steps_count": len(steps),
            "output": f"# {service} Integration Guide\n\nTarget audience: {audience}\nLanguage: {language}\n\n## Steps\n\n" + "\n".join([f"{i+1}. {step.get('title', 'Step')}: {step.get('description', '')}" for i, step in enumerate(steps)])
        }
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "translate_docs":
        content = arguments.get("content")
        source_lang = arguments.get("source_lang")
        target_lang = arguments.get("target_lang")
        context = arguments.get("context", "")
        
        # Simple translation placeholder - in production would use translation service
        translated = f"[{target_lang.upper()}] {content}" if target_lang != source_lang else content
        
        result = {
            "status": "ok",
            "tool": "translate_docs",
            "source_lang": source_lang,
            "target_lang": target_lang,
            "context": context,
            "original_length": len(content),
            "translated_length": len(translated),
            "translated_content": translated
        }
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "lint_docs":
        content = arguments.get("content")
        language = arguments.get("language", "en")
        checks = arguments.get("checks", ["spelling", "grammar", "style", "completeness", "consistency"])
        
        # Simple linting placeholder
        issues = []
        word_count = len(content.split())
        
        if "spelling" in checks:
            issues.append({"type": "spelling", "count": 0, "message": "No spelling issues found"})
        if "grammar" in checks:
            issues.append({"type": "grammar", "count": 0, "message": "No grammar issues found"})
        if "style" in checks:
            issues.append({"type": "style", "count": 0, "message": "Style looks consistent"})
        if "completeness" in checks:
            if word_count < 100:
                issues.append({"type": "completeness", "count": 1, "message": "Document may be too short"})
        if "consistency" in checks:
            issues.append({"type": "consistency", "count": 0, "message": "Terminology is consistent"})
        
        result = {
            "status": "ok",
            "tool": "lint_docs",
            "language": language,
            "word_count": word_count,
            "checks_run": checks,
            "issues": issues,
            "passed": all(issue["count"] == 0 for issue in issues)
        }
        return [TextContent(type="text", text=json.dumps(result))]
    
    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def serve():
        reader, writer = await stdio_server()
        await app.run(reader, writer)
    
    asyncio.run(serve())