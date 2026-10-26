# mcp-docs-service

MCP server for technical documentation writing and translation (FR/EN).

## Tools

### write_api_docs
Generate API documentation from endpoint definitions.

**Parameters:**
- `project` (string, required): Project name
- `endpoints` (array, required): API endpoints to document
- `language` (string, optional): "en" or "fr" (default: "en")
- `format` (string, optional): "markdown" or "openapi" (default: "markdown")

### write_integration_guide
Generate integration guide for a service.

**Parameters:**
- `service` (string, required): Service name
- `steps` (array, required): Integration steps
- `language` (string, optional): "en" or "fr" (default: "en")
- `audience` (string, optional): "developer", "admin", or "user" (default: "developer")

### translate_docs
Translate documentation between English and French.

**Parameters:**
- `content` (string, required): Content to translate
- `source_lang` (string, required): "en" or "fr"
- `target_lang` (string, required): "en" or "fr"
- `context` (string, optional): Context for translation

### lint_docs
Check documentation for quality issues.

**Parameters:**
- `content` (string, required): Documentation content to check
- `language` (string, optional): "en" or "fr" (default: "en")
- `checks` (array, optional): Checks to run - spelling, grammar, style, completeness, consistency (default: all)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Connecting to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docs-service": {
      "command": "python",
      "args": ["/path/to/mcp-docs-service/main.py"],
      "cwd": "/path/to/mcp-docs-service"
    }
  }
}
```

## License

MIT