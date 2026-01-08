# LSP Server Integration Guide for AI Coding Agents
## Comprehensive Technical Reference

**Date:** January 7, 2026  
**Document Status:** COMPLETE RESEARCH SYNTHESIS  
**Scope:** LSP server selection and integration strategies for Claude Code, Opencode, Codex, and Gemini

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Best-in-Class LSP Servers (2025)](#best-in-class-lsp-servers-2025)
3. [Integration: Claude Code](#integration-claude-code)
4. [Integration: Opencode CLI Agent](#integration-opencode-cli-agent)
5. [Integration: Codex & Gemini APIs](#integration-codex--gemini-apis)
6. [Integration: IDE Assistants (Copilot, Gemini Code Assist)](#integration-ide-assistants)
7. [Multi-Language Configuration Examples](#multi-language-configuration-examples)
8. [Performance & Best Practices](#performance--best-practices)

---

## Executive Summary

Language Server Protocol (LSP) provides AI coding agents with **semantic understanding** of codebases instead of relying solely on text search. This document provides concrete guidance on:

- **Which LSP servers** to use for each programming language (with 2025 recommendations)
- **How to configure** LSP for different agent platforms
- **Integration patterns** for Claude Code, Opencode, raw models (Codex/Gemini), and IDE-based assistants
- **Performance considerations** and optimization strategies

### Key Finding

Modern AI coding agents fall into two categories:

| Agent Type | Integration Pattern | Best Practice |
|:--|:--|:--|
| **Standalone CLI** (Claude Code, Opencode) | Configuration file (`.lsp.json`) | Direct LSP server management |
| **Raw Models** (OpenAI, Google) | Programmatic tool invocation | Build LSP client library integration |
| **IDE-Based** (Copilot, Gemini Assist) | IDE state management | Ensure IDE LSP is healthy |

---

## Best-in-Class LSP Servers (2025)

### Recommended Servers by Language

| Language | Recommended Server | Alternative | Why Best for Agents |
|:--|:--|:--|:--|
| **Python** | `pyright` | `basedpyright`, `python-lsp-server` | Fast, minimal latency, excellent type inference |
| **TypeScript/JavaScript** | `vtsls` | `typescript-language-server` | Optimized wrapper around tsserver; better resource management for agents |
| **Rust** | `rust-analyzer` | `rls` | Official tool; semantic understanding of Rust's type system |
| **Go** | `gopls` | None (standard) | Official LSP; extremely reliable |
| **C/C++** | `clangd` | `ccls` | Industry standard; excellent type information |
| **Java** | `jdtls` | `language-server` | Full Java semantic understanding |
| **PHP** | `intelephense` | `php-language-server` | Fast, accurate PHP type checking |
| **Ruby** | `ruby-lsp` | `solargraph` | Modern, maintained by Ruby maintainers |
| **C#** | `omnisharp-roslyn` | `csharp-ls` | Complete C# and .NET support |
| **YAML** | `yaml-language-server` | None | Schema validation and autocompletion |

### Installation Commands

```bash
# Python
pip install pyright
# Or: pip install basedpyright

# TypeScript/JavaScript (recommended)
npm install -g @vtsls/language-server
# Or: npm install -g typescript-language-server

# Rust
rustup component add rust-analyzer

# Go
go install golang.org/x/tools/gopls@latest

# C/C++
apt-get install clangd  # Ubuntu/Debian
brew install llvm      # macOS (then use $(brew --prefix llvm)/bin/clangd)

# Java
# Download from https://github.com/eclipse/eclipse.jdt.ls/wiki/Running-the-Java-LS-server-from-the-command-line

# PHP
composer require felixbecker/language-server

# Ruby
gem install ruby-lsp

# C#
git clone https://github.com/OmniSharp/omnisharp-roslyn.git
cd omnisharp-roslyn && ./build.sh

# YAML
npm install -g yaml-language-server
```

### Multi-LSP Strategy

For agents working with **polyglot codebases**, combine LSPs:

```bash
# Recommended modern stack
pyright          # Python
@vtsls/language-server  # TypeScript
gopls            # Go
rust-analyzer    # Rust
ruff server      # Python linting (complementary)
```

---

## Integration: Claude Code

Claude Code supports LSP natively via the `.lsp.json` configuration file and built-in LSP tools.

### Setup Steps

#### 1. Create `.lsp.json`

Place this file at your **project root** or **plugin root** (if using Claude Code plugins):

```json
{
  "python": {
    "command": "pyright",
    "args": ["--outputjson"],
    "extensionToLanguage": {
      ".py": "python"
    }
  },
  "typescript": {
    "command": "vtsls",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescript",
      ".js": "javascript",
      ".jsx": "javascript"
    }
  },
  "go": {
    "command": "gopls",
    "args": [],
    "extensionToLanguage": {
      ".go": "go"
    }
  },
  "rust": {
    "command": "rust-analyzer",
    "args": [],
    "extensionToLanguage": {
      ".rs": "rust"
    }
  }
}
```

#### 2. Update `.claude/CLAUDE.md`

Add high-level LSP guidance to your Claude Code project file:

```markdown
# Project Setup (LSP Enabled)

This project uses Language Server Protocol (LSP) for semantic code navigation.

## Available LSP Features

- **Go to Definition**: Jump to symbol definitions across files
- **Find References**: Locate all usages of a symbol
- **Hover Information**: View type signatures and documentation

## Best Practices

When asking Claude Code for code analysis:

1. Prefer **symbol-based** questions over text search
   - ❌ "Search the codebase for authenticate"
   - ✅ "Use LSP find-references on the authenticate function"

2. Use LSP before refactoring
   - "Use LSP find-references to show all callers of this function"
   - "Use LSP hover to confirm the parameter types"

3. Ask Claude to verify type safety
   - "Use LSP hover on all call sites to verify type compatibility"
```

#### 3. Create LSP-Aware Sub-Agents

Create specialized sub-agents in `.claude/agents/`:

**`.claude/agents/lsp-navigator/AGENT.md`:**

```yaml
***
name: lsp-navigator
description: >
  Uses Language Server Protocol to navigate code. Employs go-to-definition,
  find-references, and hover to understand symbol definitions and usages
  across the codebase.
tools: Read, Bash, Grep
model: inherit
***

# LSP Code Navigator

You specialize in navigating code using LSP tools.

## Process for Code Navigation

When the user asks about a symbol, function, class, or type:

1. **Locate**: Use go-to-definition to find where it is declared
2. **Understand**: Use hover to see its type signature and documentation
3. **Find Usage**: Use find-references to enumerate all usages
4. **Analyze**: Group references by file, module, and usage pattern
5. **Report**: Present definition location, type info, and usage summary

## Key LSP Operations

- `goToDefinition(symbol)` → Returns file:line of declaration
- `findReferences(symbol)` → Returns list of all usages with location context
- `hover(symbol)` → Returns type information and documentation
```

**`.claude/agents/type-checker/AGENT.md`:**

```yaml
***
name: type-checker
description: >
  Verifies type safety using LSP hover and diagnostics. Checks that parameter
  types match call sites and function signatures are consistent.
tools: Read, Bash, Grep
model: inherit
***

# LSP Type Safety Checker

You verify type safety of code changes.

## Type Checking Process

For each modified function or type:

1. Use go-to-definition to locate the declaration
2. Use hover to extract parameter and return types
3. Use find-references to list all call sites
4. For each call site:
   - Use hover on arguments to infer their types
   - Compare with function parameter types
   - Flag any incompatibilities
5. Classify issues: Critical (type mismatch) | Warning (implicit conversion) | Info (missing annotation)
```

#### 4. Add LSP-Based Skills

Create skills in `.claude/skills/`:

**`.claude/skills/lsp-symbol-navigation/SKILL.md`:**

```markdown
***
name: lsp-symbol-navigation
description: >
  Navigates code using LSP. When you ask where something is defined or how
  it is used, this skill uses go-to-definition, find-references, and hover
  to provide semantic answers.
allowed-tools: Read, Bash, Grep
***

# LSP Symbol Navigation Skill

## When to Use

- "Where is this function/class defined?"
- "What code calls this function?"
- "How is this type used across the project?"

## Navigation Steps

1. Use go-to-definition to find the definition
2. Use hover on the definition to get signature and docs
3. Use find-references to list all usages
4. Group usages by file/module
5. Present: definition location, signature, and reference summary
```

#### 5. Configure Hooks for Validation

Create `.claude/hooks/hooks.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/lsp-type-check.py"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'which pyright vtsls gopls rust-analyzer 2>/dev/null | wc -l | xargs -I {} echo \"LSP Servers Available: {}\"'"
          }
        ]
      }
    ]
  }
}
```

### Prompting Patterns for Claude Code

**Pattern 1: Symbol Navigation**

```
User: "Show me where authenticate() is defined and how it's used"

Ideal Claude Response:
1. Uses LSP go-to-definition on "authenticate"
2. Shows definition location and type signature via hover
3. Uses LSP find-references to list all call sites
4. Groups references by module
5. Presents structured output
```

**Pattern 2: Impact Analysis**

```
User: "What breaks if I rename this type?"

Ideal Claude Response:
1. Uses go-to-definition to confirm the type
2. Uses find-references to show all usages
3. Classifies each usage by risk level
4. Highlights public APIs or type-critical sites
5. Returns: count, files affected, and risk assessment
```

**Pattern 3: Type Safety Verification**

```
User: "Is this refactor type-safe?"

Ideal Claude Response:
1. Uses hover on changed function signatures
2. Uses find-references to list all call sites
3. Verifies each call site is type-compatible
4. Reports critical issues vs warnings
5. Suggests specific fixes if problems found
```

---

## Integration: Opencode CLI Agent

**Opencode** (opencode.ai) is an open-source Claude Code alternative with **native LSP support**.

### Setup Steps

#### 1. Install Opencode

```bash
pip install opencode
# Or: npm install -g @opencode/cli
```

#### 2. Configure LSP (Two Options)

**Option A: Auto-Detection (Recommended)**

Opencode automatically detects and configures these LSP servers:

- `pyright` (Python)
- `gopls` (Go)
- `rust-analyzer` (Rust)
- `typescript-language-server` (TypeScript)
- `jdtls` (Java)
- And 20+ others

Simply have them installed:

```bash
pip install pyright
npm install -g @vtsls/language-server
rustup component add rust-analyzer
go install golang.org/x/tools/gopls@latest
```

**Option B: Custom Configuration**

Create `opencode.toml` or `config.toml` in your project root:

```toml
[lsp]
python = "pyright"
typescript = "vtsls"
go = "gopls"
rust = "rust-analyzer"

[lsp.options]
# Optional: custom arguments per LSP
python_args = ["--outputjson"]
typescript_args = ["--stdio"]

[lsp.disabled]
# Disable specific LSPs if needed
languages = ["php"]
```

#### 3. Enable LSP Tools

Start Opencode with LSP enabled:

```bash
opencode --enable-lsp
# Or set environment variable:
export ENABLE_LSP=1
opencode
```

#### 4. Use LSP in Opencode

Once running, you can prompt Opencode with LSP-aware requests:

```
> find all uses of the User type using LSP find-references
> show me where authenticate is defined using go-to-definition
> verify type safety on this file using LSP diagnostics
```

### Key Differences from Claude Code

| Feature | Claude Code | Opencode |
|:--|:--|:--|
| LSP Config | `.lsp.json` | `opencode.toml` or auto-detection |
| Auto-Server Discovery | No | Yes (native) |
| Sub-agents | Yes | Planned |
| Skills System | Yes | Native CLI skills |
| Hooks | Yes | Event handlers |
| Plugin System | Yes | Planned |

### Prompting Patterns for Opencode

```
# Navigation
opencode "use lsp find-references on the Config class"

# Type Checking  
opencode "use lsp hover to show parameter types in this file"

# Dependency Analysis
opencode "use lsp to find all importers of this module"

# Refactoring Safety
opencode "before renaming this function, show me all references using lsp find-references"
```

---

## Integration: Codex & Gemini APIs

When using **raw models** (OpenAI Codex, Google Gemini), you must build an LSP client layer that the agent can invoke programmatically.

### Architecture Pattern

```
┌─────────────────────────┐
│  Agent (GPT-4/Gemini)   │
│   Uses tool_call to     │
│  fetch symbol info      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   LSP Client Library    │
│  (multilspy or custom)  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   LSP Servers           │
│ pyright, gopls, etc.    │
└─────────────────────────┘
```

### Implementation with `multilspy` Library

**Installation:**

```bash
pip install multilspy
```

**Example: Codex with LSP Backend**

```python
import json
from multilspy.multilspy_server import MultilspyServer, MultilspyServerConfig
import anthropic

# Initialize LSP servers
server_config = MultilspyServerConfig.from_sys_info()
lsp = MultilspyServer(server_config=server_config)

# Connect to repository
lsp.initialize_repo(
    repo_path="/path/to/repo",
    languages=["python", "typescript"]
)

client = anthropic.Anthropic()

# Define LSP tools for Claude
tools = [
    {
        "name": "go_to_definition",
        "description": "Find where a symbol is defined",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "line": {"type": "integer"},
                "column": {"type": "integer"},
                "symbol": {"type": "string"}
            },
            "required": ["file_path", "symbol"]
        }
    },
    {
        "name": "find_references",
        "description": "Find all usages of a symbol",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "symbol": {"type": "string"}
            },
            "required": ["file_path", "symbol"]
        }
    },
    {
        "name": "hover_info",
        "description": "Get type information for a symbol",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "line": {"type": "integer"},
                "column": {"type": "integer"},
                "symbol": {"type": "string"}
            },
            "required": ["file_path", "symbol"]
        }
    }
]

# Agentic loop
messages = [
    {
        "role": "user",
        "content": "Find where the User class is defined and show me all places it's instantiated"
    }
]

system_prompt = """You are a code analysis agent with access to Language Server Protocol (LSP) tools.
When analyzing code:
1. Use go_to_definition to find symbol definitions
2. Use hover_info to understand types and signatures
3. Use find_references to locate all usages
Report findings in a structured format."""

while True:
    response = client.messages.create(
        model="gpt-4",
        max_tokens=2048,
        system=system_prompt,
        tools=tools,
        messages=messages
    )
    
    # Check if we need to process tool calls
    if response.stop_reason == "tool_use":
        # Process each tool call
        tool_results = []
        for content_block in response.content:
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input
                
                # Execute LSP operations
                if tool_name == "go_to_definition":
                    result = lsp.go_to_definition(
                        document_path=tool_input["file_path"],
                        line=tool_input.get("line", 0),
                        character=tool_input.get("column", 0)
                    )
                elif tool_name == "find_references":
                    result = lsp.find_references(
                        document_path=tool_input["file_path"],
                        line=tool_input.get("line", 0),
                        character=tool_input.get("column", 0)
                    )
                elif tool_name == "hover_info":
                    result = lsp.hover(
                        document_path=tool_input["file_path"],
                        line=tool_input.get("line", 0),
                        character=tool_input.get("column", 0)
                    )
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": json.dumps(result, indent=2)
                })
        
        # Add assistant response and tool results to messages
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
    
    else:
        # Model has finished (stop_reason == "end_turn")
        final_response = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None
        )
        print("Agent Response:")
        print(final_response)
        break
```

### Implementation for Google Gemini

```python
import json
import anthropic
import google.generativeai as genai
from multilspy.multilspy_server import MultilspyServer

# Initialize Gemini
genai.configure(api_key="YOUR_GEMINI_API_KEY")

lsp_server = MultilspyServer()
lsp_server.initialize_repo("/path/to/repo")

# Define tools for Gemini
lsp_tools = [
    {
        "type": "function",
        "function": {
            "name": "lsp_go_to_definition",
            "description": "Find symbol definition using LSP",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "symbol": {"type": "string"}
                }
            }
        }
    },
    # ... other tools
]

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    tools=lsp_tools
)

# Chat with Gemini
chat = model.start_chat()

response = chat.send_message(
    """Analyze the authentication flow in this codebase.
    Find the main auth function and show all functions it calls.
    Use LSP tools to provide exact locations and type information."""
)

# Process tool calls
while True:
    if response.candidates[0].content.parts[-1].function_call:
        # Process function calls and continue
        pass
    else:
        print(response.text)
        break
```

---

## Integration: IDE Assistants

### Copilot Integration

**GitHub Copilot** runs as an IDE extension and leverages the **IDE's built-in LSP client**.

**Best Integration Practice:**

1. **Ensure VS Code/JetBrains has healthy LSP configuration**
   ```json
   // VS Code settings.json
   {
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "[python]": {
       "editor.defaultFormatter": "ms-python.python",
       "editor.formatOnSave": true
     },
     "typescript.suggest.enabled": true
   }
   ```

2. **Install recommended language extensions**
   - Python: **Pylance** (includes Pyright)
   - TypeScript: **Official TypeScript extension**
   - Go: **Go extension by Google**
   - Rust: **rust-analyzer extension**

3. **Copilot automatically leverages IDE state** – no separate LSP config needed

### Gemini Code Assist Integration

**Gemini Code Assist** uses the IDE's LSP infrastructure via Google Cloud's integration.

**Best Integration Practice:**

1. **Install Gemini Code Assist extension** for VS Code / IntelliJ
2. **Ensure your project has healthy type information**
   ```bash
   # For Python
   pip install pyright
   
   # For TypeScript
   npm install --save-dev typescript
   ```

3. **Grant Gemini access to your codebase** (via IDE extension settings)

4. **Gemini automatically indexes your code** and uses LSP diagnostics

---

## Multi-Language Configuration Examples

### Complete `.lsp.json` for a Polyglot Project

```json
{
  "python": {
    "command": "pyright",
    "args": ["--outputjson"],
    "extensionToLanguage": {
      ".py": "python",
      ".pyx": "python"
    }
  },
  "typescript": {
    "command": "vtsls",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescript",
      ".js": "javascript",
      ".jsx": "javascript"
    }
  },
  "go": {
    "command": "gopls",
    "args": ["-mode=stdio"],
    "extensionToLanguage": {
      ".go": "go"
    }
  },
  "rust": {
    "command": "rust-analyzer",
    "args": [],
    "extensionToLanguage": {
      ".rs": "rust"
    }
  },
  "java": {
    "command": "jdtls",
    "args": ["-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=1044"],
    "extensionToLanguage": {
      ".java": "java"
    }
  },
  "cpp": {
    "command": "clangd",
    "args": ["--header-insertion=iwyu"],
    "extensionToLanguage": {
      ".cpp": "cpp",
      ".cc": "cpp",
      ".cxx": "cpp",
      ".h": "cpp",
      ".hpp": "cpp"
    }
  }
}
```

### Multi-Server Strategy with Linting

For enhanced validation, pair type checkers with linters:

```json
{
  "python": {
    "command": "pyright",
    "args": ["--outputjson"],
    "extensionToLanguage": { ".py": "python" }
  },
  "python-linter": {
    "command": "ruff",
    "args": ["server"],
    "extensionToLanguage": { ".py": "python" }
  },
  "typescript": {
    "command": "vtsls",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescript"
    }
  },
  "typescript-linter": {
    "command": "eslint",
    "args": ["--stdin", "--stdin-filename"],
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescript"
    }
  }
}
```

---

## Performance & Best Practices

### Optimization Strategies

1. **Keep LSP Servers Running**
   ```bash
   # DON'T: restart server for each query
   # DO: keep single long-running process
   # Claude Code and Opencode handle this automatically
   ```

2. **Cache Symbol Information**
   ```python
   # Example: cache go-to-definition results
   _definition_cache = {}
   
   def get_definition(symbol):
       if symbol in _definition_cache:
           return _definition_cache[symbol]
       result = lsp.go_to_definition(symbol)
       _definition_cache[symbol] = result
       return result
   ```

3. **Batch LSP Requests**
   ```python
   # Query multiple symbols in one pass
   references = lsp.find_references(["User", "Config", "Auth"])
   # vs. querying each individually
   ```

4. **Limit Reference Results**
   ```python
   # For popular symbols, limit results
   refs = lsp.find_references("get", max_results=100)
   # Filter by file pattern if needed
   refs = [r for r in refs if "test" not in r.file_path]
   ```

5. **Prioritize Server Installation**
   - Install LSP servers on **local machine** (don't network them)
   - Use **fast servers**: `pyright` > `python-lsp-server`; `vtsls` > `typescript-language-server`
   - Disable unused languages in `.lsp.json`

### Common Pitfalls & Solutions

| Pitfall | Cause | Solution |
|:--|:--|:--|
| LSP "not found" | Server not installed | Run install command; verify with `which` |
| Slow responses | Server starting on each query | Keep server resident; verify `.lsp.json` |
| Type info incomplete | Untyped/weak typing in project | Add type annotations; use type hints |
| Too many references | Searching on common names | Combine go-to-definition + hover first |
| Circular dependency errors | LSP server misconfigured | Simplify `.lsp.json`; test server in CLI |

### Verification Checklist

```bash
# 1. Verify LSP servers are installed
pyright --version
vtsls --version
gopls version
rust-analyzer --version

# 2. Test LSP locally
pyright src/main.py --outputjson | head

# 3. Verify .lsp.json syntax
python -m json.tool .lsp.json > /dev/null && echo "Valid JSON"

# 4. Check Claude Code can find .lsp.json
find . -name ".lsp.json" -type f

# 5. Test in Claude Code
# Start Claude Code and ask: "Use LSP to find where [symbol] is defined"
```

---

## Conclusion

**Best Integration Path:**

1. **Claude Code Users** → Create `.lsp.json`, use recommended servers, adopt LSP-aware prompting
2. **Opencode Users** → Install servers, let auto-detection work, use CLI with LSP flags
3. **Raw Model Users** → Build LSP client layer with `multilspy`, expose as tools
4. **IDE Assistant Users** → Install language extensions, ensure healthy IDE LSP configuration

By leveraging LSP effectively, your AI coding agents gain **IDE-level code understanding** while remaining **language-agnostic** and **repository-independent**.
