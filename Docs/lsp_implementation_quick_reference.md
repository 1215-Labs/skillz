<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# lsp_implementation_quick_reference.md

Here is the full `lsp_implementation_quick_reference.md` content you can drop into your repo (for example `docs/lsp_implementation_quick_reference.md` or `.claude/docs/lsp_implementation_quick_reference.md`).

```markdown
# Claude Code LSP Implementation: Quick Reference Guide

**One-page quick lookup for LSP integration patterns**

---

## LSP CONFIGURATION CHECKLIST

```bash
# 1. Install LSP servers (example set)

pip install pyright                          # Python
npm install -g typescript-language-server    # TypeScript/JavaScript
go install golang.org/x/tools/gopls@latest   # Go
rustup component add rust-analyzer           # Rust

# 2. Enable the LSP tool if required

# (depending on your environment / plugin setup)

export ENABLE_LSP_TOOL=1                     # e.g., per some guides[^1][^2]

# 3. Create .lsp.json in repo or plugin root

cat > .lsp.json << 'EOF'
{
  "python": {
    "command": "pyright",
    "args": ["--outputjson"],
    "extensionToLanguage": { ".py": "python" }
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
EOF

# 4. Verify language servers are installed

which pyright typescript-language-server gopls rust-analyzer || echo "Some LSPs missing"

# 5. Run Claude Code with LSP enabled

claude                                   # or `claude -p "explain this repo"`
```


---

## PROMPTING PATTERN TEMPLATES

### Pattern 1: Navigate Code

```text
User: "Show me the code path from [entry_point] to [target_function]."

Claude should:
1. Use LSP go-to-definition on [entry_point].
2. Follow calls, using go-to-definition at each step, until [target_function].
3. Use hover on each function to show signatures.
4. Optionally use find-references on [target_function] to show all callers.
5. Return a summarized call chain: file:line → file:line → …
```


### Pattern 2: Assess Change Impact

```text
User: "What breaks if I rename [symbol]?"

Claude should:
1. Use go-to-definition on [symbol] to confirm its definition.
2. Use find-references to list all usages of [symbol].
3. Group references by file/module.
4. Highlight high-risk usages (e.g., type-sensitive sites, public APIs).
5. Return: total references, per-file counts, and a short risk summary.
```


### Pattern 3: Verify Type Safety

```text
User: "Is this change type-safe?"

Claude should:
1. Use hover on modified function/TypeScript type definitions to get signatures.[^1]
2. Use find-references to list all call sites / usages.
3. For each call site, compare argument types vs parameter types via hover.
4. Flag mismatches (critical) and implicit conversions/nullability issues (warnings).
5. Return a small report: Critical / Warnings / Info.
```


### Pattern 4: Map Dependencies

```text
User: "What depends on [module_or_type]?"

Claude should:
1. Use go-to-definition on [module_or_type] to confirm the symbol.
2. Use find-references to list all importers or implementors.
3. Group by module / layer (e.g., api, service, data).
4. Return: inbound dependencies (who uses it), plus any obvious cycles or hotspots.
```


---

## SUB-AGENT QUICK TEMPLATES

### Agent 1: LSP Navigator

```yaml
***
name: lsp-navigator
description: >
  Navigate code using LSP go-to-definition, find-references, and hover. Use this
  agent to find where things are defined, how they are used, and how code flows
  across modules.
tools: Read, Bash, Grep
model: inherit
***
# LSP Navigator

You are a code navigation specialist using Language Server Protocol (LSP).

When the user asks where something is or how code pieces connect:

1. Use go-to-definition to locate symbol definitions.
2. Use hover on definitions to understand signatures and docs.
3. Use find-references to list all usages across the project.
4. Group results by file/module and usage type.
5. Present a concise explanation of how the symbol is used and what depends on it.
```


### Agent 2: Dependency Analyzer

```yaml
***
name: dependency-analyzer
description: >
  Analyze code dependencies using LSP. Uses find-references and go-to-definition
  to see who depends on what. Use this agent for refactors and architecture reviews.
tools: Read, Bash, Grep
model: inherit
***
# Dependency Analyzer

You analyze dependencies between modules and types using LSP.

Given a module, file, or symbol:

1. Use file reading to list imports (direct dependencies).
2. Use go-to-definition to resolve imported symbols.
3. Use find-references on the target to find reverse dependencies.
4. Build a dependency picture: outbound (imports) and inbound (dependents).
5. Detect high-coupling hotspots and potential circular dependencies.
6. Summarize risk and refactoring suggestions.
```


### Agent 3: Type Checker

```yaml
***
name: type-checker
description: >
  Check type safety using LSP hover and diagnostics. Use this agent before merge
  or deploy to catch type mismatches and unsafe changes.
tools: Read, Bash, Grep
model: inherit
***
# Type Checker

You verify type safety for code changes using LSP.

When reviewing changes:

1. Use go-to-definition to find changed functions/types.
2. Use hover to read parameter and return types.
3. Use find-references to list call sites.
4. For each call site, compare actual argument types with expected types.
5. Flag mismatches and nullability issues.
6. Present a short report with locations and recommended fixes.
```


---

## HOOK SCRIPT SNIPPETS

### Hook 1: Post-edit Type Check (lightweight)

`.claude/hooks/hooks.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/lsp-type-check.py"
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/lsp-type-check.py`:

```python
#!/usr/bin/env python3
import json, sys, subprocess

def main():
  data = json.load(sys.stdin)
  file_path = data.get("tool_input", {}).get("file_path", "")
  if not file_path:
    print("No file_path, skipping LSP type check")
    return

  # Example: call pyright on the single file (adjust per language)
  proc = subprocess.run(
    ["pyright", "--outputjson", file_path],
    capture_output=True,
    text=True
  )
  if proc.returncode not in (0, 1):
    print("LSP type check failed unexpectedly", file=sys.stderr)
    return

  try:
    result = json.loads(proc.stdout)
  except Exception:
    print("Could not parse pyright JSON output", file=sys.stderr)
    return

  diags = result.get("generalDiagnostics", [])
  if not diags:
    print("✓ LSP type check passed")
    return

  print("⚠️ LSP type check issues:")
  for d in diags[:20]:
    f = d.get("file", file_path)
    msg = d.get("message", "")
    sev = d.get("severity", "warning")
    line = d.get("range", {}).get("start", {}).get("line", "?")
    print(f"  [{sev}] {f}:{line} - {msg}")

if __name__ == "__main__":
  main()
```


### Hook 2: Pre-edit Reference Impact Warning

`.claude/hooks/hooks.json` (additional entry):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/lsp-reference-impact.py"
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/lsp-reference-impact.py` (skeleton):

```python
#!/usr/bin/env python3
import json, sys, subprocess

def extract_symbols(tool_input: dict):
  # Simplified: real implementation would parse diff or content.
  return tool_input.get("symbol_names", [])

def main():
  data = json.load(sys.stdin)
  ti = data.get("tool_input", {})
  file_path = ti.get("file_path", "")
  symbols = extract_symbols(ti)
  if not (file_path and symbols):
    print("No symbols to check, skipping impact analysis")
    return

  high_impact = []
  for sym in symbols:
    # Replace with your LSP client wrapper
    proc = subprocess.run(
      ["lsp-client", "findReferences", file_path, sym],
      capture_output=True,
      text=True
    )
    if proc.returncode != 0:
      continue
    refs = [l for l in proc.stdout.splitlines() if l.strip()]
    if len(refs) > 20:
      high_impact.append((sym, len(refs)))

  if high_impact:
    print("⚠️ Potentially high-impact edits (via LSP find-references):")
    for sym, cnt in sorted(high_impact, key=lambda x: -x):

![LSP Integration Strategy Flowchart](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/0d0e31f9b2505bc19b7edc5f1dfe21b3/5f7ea0f0-ea61-498e-aaa2-d810f9943dfa/eeebff9f.png)

LSP Integration Strategy Flowchart

print(f"  -  {sym}: {cnt} references")
  else:
    print("✓ No high-impact symbols detected")

if __name__ == "__main__":
  main()
```


---

## SKILL QUICK TEMPLATES

### Skill 1: LSP Symbol Navigation

`.claude/skills/lsp-symbol-navigation/SKILL.md`:

```markdown
***
name: lsp-symbol-navigation
description: >
  Navigate symbols using Language Server Protocol. Uses go-to-definition to find
  definitions, find-references to list usages, and hover to get type info. Use
  when you ask where something is defined or how it is used.
allowed-tools: Read, Bash, Grep
***

# LSP Symbol Navigation

## When to use

- "Where is this function/class defined?"
- "What code calls this function?"
- "How is this type used across the project?"

## Process

1. Use go-to-definition on the symbol to find the definition.
2. Use hover on the definition to get its type signature and docs.
3. Use find-references to list all usages.
4. Group references by file/module and usage type.
5. Return: definition location, signature, and reference summary.
```


### Skill 2: LSP Dependency Analysis

```markdown
***
name: lsp-dependency-analysis
description: >
  Analyze dependencies using LSP. Uses find-references and go-to-definition to
  see who imports or calls a module or type. Use for refactors and architecture
  review.
allowed-tools: Read, Bash, Grep, Write
***

# LSP Dependency Analysis

## When to use

- "What depends on this module?"
- "If I change this type, who breaks?"
- "Is this module tightly coupled?"

## Process

1. Identify the target (module/file/type).
2. Use go-to-definition to confirm its declaration.
3. Use find-references to list all inbound dependencies (who uses it).
4. Optionally, list outbound deps via imports.
5. Summarize: inbound count, outbound count, and any hotspots.
```


### Skill 3: LSP Type Safety Check

```markdown
***
name: lsp-type-safety-check
description: >
  Verify type safety using LSP hover and find-references. Use before merge or
  deploy to catch type mismatches and unsafe changes.
allowed-tools: Read, Bash, Grep
***

# LSP Type Safety Check

## When to use

- "Is this PR safe in terms of types?"
- "Will changing this function break callers?"
- "Are my TS types still valid after this refactor?"

## Process

1. For each changed function/type:
   - Use go-to-definition to find the declaration.
   - Use hover to read parameter and return types.
2. Use find-references to list call sites.
3. For each call site, compare argument/return usage with the signature.
4. Classify issues as Critical / Warning / Info.
5. Return a short report with file:line and suggested fixes.
```


---

## LSP COMMAND REFERENCE (CONCEPTUAL)

| Operation | What it does |
| :-- | :-- |
| `goToDefinition` | Jump to a symbol’s definition |
| `findReferences` | Find all usages of a symbol |
| `hover` | Show type info / documentation for a symbol |
| `getDiagnostics` | Show errors/warnings (if supported) [web:12][web:31] |

In practice, these are exposed via Claude Code LSP tools or language-specific CLIs (e.g., Pyright, TS server). [web:12][web:31]

---

## REPO LAYOUT (SUGGESTED)

```text
my-project/
├── .lsp.json
├── .claude/
│   ├── CLAUDE.md
│   ├── agents/
│   │   ├── lsp-navigator/AGENT.md
│   │   ├── dependency-analyzer/AGENT.md
│   │   └── type-checker/AGENT.md
│   ├── skills/
│   │   ├── lsp-symbol-navigation/SKILL.md
│   │   ├── lsp-dependency-analysis/SKILL.md
│   │   └── lsp-type-safety-check/SKILL.md
│   └── hooks/
│       ├── hooks.json
│       ├── lsp-type-check.py
│       └── lsp-reference-impact.py
└── src/...
```

This mirrors the official layout for project Skills and agents, and for plugins you can use `skills/`, `agents/`, `hooks/`, `.lsp.json` at plugin root. [web:4][web:6]

---

## WEEKLY IMPROVEMENT LOOP (LSP SKILLS)

1. **Log usage**
    - Use a `SubagentStop` or `PostToolUse` hook to log which LSP skills/agents ran, which LSP operations they used, and whether the outcome was good.
2. **Analyze metrics**
    - Once a week, run a script that:
        - Groups by skill.
        - Computes success rate.
        - Finds patterns like “find-references‑only flows fail more often”.
3. **Update skills and agents**
    - Refine SKILL.md / AGENT.md instructions:
        - Add disambiguation steps.
        - Add “if too many references, filter by path” rules.
    - Increment a `version:` field in SKILL.md when you change behavior. [web:6][web:35]
4. **Re‑test**
    - Run a couple of navigation/refactor scenarios.
    - Confirm that skills trigger correctly and yield better outputs.

---

## COMMON “DO / DON’T” REMINDERS

- **Do** phrase tasks in terms of symbols and types:
    - “Use LSP to see where this type is used.”
- **Don’t** only say “search for this string in the repo.”
- **Do** create small, specialized agents for navigation, dependencies, and type checking.
- **Don’t** put every behavior into one monolithic agent.
- **Do** keep SKILL.md short and push details into separate files. [web:6]
- **Don’t** overload the main skill with long explanations and rarely used details.
- **Do** use hooks for key guardrails (impact warnings, type checks).
- **Don’t** run expensive LSP scans on every trivial edit.

---

**Last Updated:** January 7, 2026
**Based on:** Claude Code Skills, Hooks, and Plugins docs + community LSP guides. [web:6][web:8][web:4][web:12][web:31]

```

You can adjust paths (e.g. put this under `docs/` instead of `.claude/`) and trim sections as needed for your team.
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://www.aifreeapi.com/en/posts/claude-code-lsp
[^2]: https://www.youtube.com/watch?v=cPTEal0ILDI
[^3]: https://code.claude.com/docs/en/skills
[^4]: https://code.claude.com/docs/en/plugins
[^5]: https://code.claude.com/docs/en/hooks-guide
[^6]: https://code.claude.com/docs/en/cli-reference
[^7]: https://github.com/wesammustafa/Claude-Code-Everything-You-Need-to-Know
[^8]: https://sankalp.bearblog.dev/my-experience-with-claude-code-20-and-how-to-get-better-at-using-coding-agents/
[^9]: https://awesomeclaude.ai/awesome-claude-code
[^10]: https://www.reddit.com/r/ClaudeCode/comments/1pn2l6l/claude_hooks_skills_subagents_is_amazing/
[^11]: https://alexop.dev/posts/understanding-claude-code-full-stack/
[^12]: https://github.com/ktnyt/cclsp
[^13]: https://swi-prolog.discourse.group/t/using-claude-code-to-create-skills-commands-plans-for-swi-prolog/9420
[^14]: https://blog.sshh.io/p/how-i-use-every-claude-code-feature
[^15]: https://www.anthropic.com/engineering/claude-code-best-practices
[^16]: https://apidog.com/es/blog/claude-code-cheatsheet/
[^17]: https://www.reddit.com/r/ClaudeCode/comments/1ptw6fd/claude_code_jumpstart_guide_now_version_11_to/
[^18]: https://ai.gopubby.com/the-complete-guide-to-claude-as-your-coding-assistant-every-configuration-you-need-to-know-as-4d525d2907c4
[^19]: https://dev.to/damogallagher/the-ultimate-claude-code-tips-collection-advent-of-claude-2025-5b73
[^20]: https://thegroundtruth.substack.com/p/my-claude-code-workflow-and-personal-tips
[^21]: https://skywork.ai/skypage/en/In-Depth-Analysis-of-lsp-mcp-MCP-Server-The-Definitive-Guide-for-AI-Engineers/1972485856809889792```

