# Claude Code LSP Integration: Research Findings

**Date:** January 7, 2026  
**Scope:** How to best leverage Language Server Protocol (LSP) with Claude Code across prompting, sub-agents, hooks, skills, repository structure, and self‑improving skills.

---

## 1. What LSP Changes In Claude Code

LSP gives Claude Code IDE‑style code intelligence over your repo rather than just file‑by‑file text scanning. In Claude Code 2.0.74+ this typically includes:

- `goToDefinition`: Jump to where a symbol is defined. [web:17][web:30]
- `findReferences`: List all usages of a symbol in the workspace. [web:17][web:30]
- `hover`: Show type info and documentation for a symbol. [web:17][web:30]
- Sometimes `documentSymbol` and diagnostics, depending on the language servers you configure. [web:17][web:31]

In practice this means:

- You can reason about **symbols** (functions, classes, types, methods) instead of string patterns.
- Navigation across large repos is **O(1)** in terms of reasoning—LSP returns exact definitions and references without scanning every file. [web:12][web:31]
- Type information is accessible via hover, which allows type‑aware review and refactoring workflows. [web:12][web:32]

### 1.1 Configuration surface in Claude Code

LSP is wired into Claude Code via:

- A project‑ or plugin‑scoped `.lsp.json` file that declares language servers. [web:4]
- LSP “tools” that Claude can call internally for go‑to‑definition / find‑refs / hover. [web:31][web:32]
- Optional environment flags or plugin install steps to enable language‑specific servers (e.g. TypeScript or Pyright plugins). [web:31][web:12]

Example `.lsp.json` at project or plugin root:

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
    "command": "typescript-language-server",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescript"
    }
  }
}
