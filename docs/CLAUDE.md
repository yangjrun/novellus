# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This repository contains a Model Control Protocol (MCP) server implementation using the Python FastMCP SDK. The server is named "Novellus MCP Server" and provides file operations, calculation tools, and prompt generation capabilities.

### Core Components

- **mcp_server.py**: Main server implementation with FastMCP framework
  - File operations: read_file resource, create_file and list_directory tools
  - Calculator tool with basic mathematical expression evaluation
  - Prompt generators for greetings and code reviews
  - Signal handling for graceful shutdown
- **config.py**: Configuration management using environment variables
  - MCPConfig class for server settings
  - Server name configurable via MCP_SERVER_NAME environment variable

### MCP Server Structure

The server implements:
- **Resources**: file:// protocol for reading local files
- **Tools**: calculate(), list_directory(), create_file()
- **Prompts**: generate_greeting(), code_review_prompt()

## Development Commands

### Running the Server
```bash
python mcp_server.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
- `MCP_SERVER_NAME`: Server name (defaults to "Novellus MCP Server")

## Key Dependencies

- mcp[cli]>=1.0.0: MCP Python SDK with CLI support
- pydantic>=2.0.0: Data validation library

## Server Transport

The server uses stdio transport for communication, making it suitable for integration with MCP clients that communicate over standard input/output.