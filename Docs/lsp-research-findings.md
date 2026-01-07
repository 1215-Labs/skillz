<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# - Full, verbose “research findings” document (longest, lots of examples)

Below is a full, verbose “research findings” document you can paste into `docs/lsp_research_findings.md` (or anywhere you like). It’s self-contained and designed to be long and example‑heavy.

```markdown
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
```

For plugins, `.lsp.json` lives in the plugin root alongside `skills/`, `agents/`, `hooks/`, etc. [web:4]

---

## 2. Prompting: How To Talk To Claude When LSP Exists

With LSP, the biggest mistake is still prompting as if Claude only has grep and a basic file reader. To exploit LSP, prompts must:

- Ask for **symbol‑centric** operations.
- Explicitly mention **go‑to‑definition**, **find‑references**, and **hover** when describing workflows.
- Emphasize **impact analysis** and **type safety** rather than “search through the codebase”. [web:12][web:32]


### 2.1 Anti‑patterns vs good patterns

**Anti‑pattern: text‑search phrasing**

- “Search the repo for where `User` is used.”
- “Look for all occurrences of `authenticate`.”
- “Scan all files for this string.”

This pushes Claude toward reading and grepping files manually.

**LSP‑aware phrasing**

- “Use LSP **find‑references** on the `User` type and list all modules that depend on it.”
- “Use **go‑to‑definition** on `authenticate` to show where it is defined, then list all callers via **find‑references**.”
- “Use **hover** on this function to confirm its parameter and return types, then verify all call sites match.” [web:12][web:32]


### 2.2 Prompt template: LSP‑enhanced code understanding

```markdown
# LSP‑Enhanced Code Understanding

You have access to Language Server Protocol (LSP) tools for this project.

When understanding a piece of code:

1. Use **go‑to‑definition** on key symbols (functions, classes, types) to find their definitions.
2. Use **hover** on those symbols to see their type signatures and documentation.
3. Use **find‑references** on the symbol to list all usages across the project.
4. Use the references to infer:
   - Which modules depend on this symbol.
   - How it’s typically used.
   - Whether any usages look inconsistent with the type signature.

Report:

- Definition location and summary.
- Type signature (from hover).
- Number of references and rough grouping by file/module.
- Any suspicious or inconsistent usages.
```


### 2.3 Prompt template: LSP‑guided refactor

```markdown
# Safe Refactor Using LSP

I want to refactor the symbol: [symbol name].

Please:

1. Use **go‑to‑definition** to locate the definition and show the surrounding code.
2. Use **hover** to extract the current type signature (parameters, generics, return type).
3. Use **find‑references** to enumerate all call sites.
4. Group references by file/module, and identify any that:
   - Pass arguments of suspicious types.
   - Rely on deprecated behavior.
5. Propose a refactor plan that:
   - Preserves type compatibility where possible.
   - Calls out any references that will break and how to fix them.
6. After applying the refactor, use **hover** and **find‑references** again to verify:
   - All call sites still type‑check.
   - No references are left pointing to removed symbols.
```


### 2.4 Prompt template: LSP‑based impact analysis

```markdown
# Impact Analysis With LSP

Before changing this type or function, do an impact analysis using LSP:

1. Use **go‑to‑definition** to show the canonical definition.
2. Use **find‑references** to list all usages.
3. For each usage, use **hover** if needed to confirm the types involved.
4. Classify each usage as:
   - Safe under the proposed change.
   - Needs a minor update.
   - Likely to break.

Return:

- Total reference count.
- A table of [file, line, classification, note].
- A short summary of risk (“low/medium/high”) and recommended next steps.
```

These patterns teach Claude that LSP is the primary mechanism for understanding structure, not text scanning.

---

## 3. Sub‑Agents: LSP‑Specialized Personas

Sub‑agents in Claude Code are separate “personas” with their own prompts, tools, and optionally skills. [web:7][web:9][web:33] They’re ideal for encapsulating LSP‑heavy workflows so that:

- The main agent can delegate complex analysis to a specialist.
- Each sub‑agent has a narrow, well‑defined job.
- You can attach different skills/hooks to them.


### 3.1 LSP Navigator agent

**File:** `.claude/agents/lsp-navigator/AGENT.md` [web:7][web:9]

```yaml
***
name: lsp-navigator
description: >
  Uses Language Server Protocol (LSP) to navigate and understand codebases.
  Uses go-to-definition to find symbol definitions, find-references to list usages,
  and hover to retrieve type information and documentation. Use this subagent
  when you need to understand how parts of the codebase relate to each other.
tools: Read, Bash, Grep
model: inherit
***
# LSP Code Navigator

You are a specialist in navigating code using LSP.

## Capabilities

- Use **go-to-definition** to jump to symbol definitions.
- Use **find-references** to list all usages of a symbol.
- Use **hover** to see type information and documentation.
- Use file reading and minimal Grep as a fallback when LSP is missing context.

## Workflow

When the user asks about a function, class, type, or module:

1. Identify the target symbol and, if necessary, the file or namespace.
2. Use **go-to-definition** to locate the exact definition.
3. Use **hover** on the definition to extract:
   - Parameter and return types.
   - Generic parameters / constraints.
   - Any docstring or comments.
4. Use **find-references** to enumerate all usages of the symbol.
5. Group references by:
   - File/module.
   - Usage kind (call, import, implementation, test, etc.).
6. Present:
   - Definition location and summary.
   - Type signature.
   - Reference counts per file and per usage kind.
   - Any suspicious or inconsistent usages.

Prefer LSP over text search. Only fall back to Grep when LSP cannot resolve a symbol.
```


### 3.2 Dependency Analyzer agent

```yaml
***
name: dependency-analyzer
description: >
  Analyzes module and type dependencies using LSP. Uses find-references to map
  who depends on what, and go-to-definition to trace dependency chains. Use this
  subagent for refactors, architecture reviews, and impact analysis.
tools: Read, Bash, Grep
model: inherit
***
# LSP Dependency Analyzer

You map dependencies using LSP.

## Responsibilities

- Identify direct and indirect dependencies between modules.
- Measure coupling via reference counts.
- Detect circular dependencies and risky hub modules.

## Process

Given a module, symbol, or file path:

1. List its direct imports (via file reading).
2. For each imported symbol or module, use **go-to-definition** to confirm.
3. Use **find-references** on the target to find all reverse dependencies:
   - Files that import or reference it.
   - Types implementing interfaces.
4. Construct:
   - A list of “imports” (outgoing edges).
   - A list of “dependents” (incoming edges).
5. Highlight:
   - Highly coupled modules (many dependents).
   - Circular dependencies (A → B → A).
   - Orphaned modules (no dependents, no imports).
6. Provide a concise dependency report and refactoring suggestions.
```


### 3.3 Type Checker sub‑agent

```yaml
***
name: type-checker
description: >
  Verifies type safety of code changes using LSP hover and references.
  Uses hover to inspect function/type signatures and find-references to
  ensure all call sites remain compatible. Use this subagent before merging
  or deploying changes to catch type errors early.
tools: Read, Bash, Grep
model: inherit
***
# LSP Type Safety Checker

You review changes for type safety using LSP.

## Process

For each modified function, method, or type:

1. Use **go-to-definition** to locate the declaration.
2. Use **hover** on the declaration to get:
   - Parameter types.
   - Return type.
   - Type parameters and constraints.
3. Use **find-references** to list all call sites and usages.
4. For each call site:
   - Use **hover** on arguments to infer their types.
   - Compare argument types with parameter types.
   - Check return handling (e.g. nullable vs non-nullable).
5. Classify issues:
   - Critical: type mismatch, missing required arg, incompatible return type.
   - Warning: implicit conversions, unsafe null handling.
   - Info: missing annotations, overly broad types.
6. Produce a structured report with locations and suggested fixes.
```


### 3.4 Connecting skills to sub‑agents

Sub‑agents can preload specific skills via a `skills:` field in the frontmatter. [web:7][web:6]

Example:

```yaml
***
name: architecture-reviewer
description: >
  Reviews architecture using LSP-based dependency analysis.
tools: Read, Bash, Grep
skills: lsp-dependency-analysis, lsp-symbol-navigation
model: inherit
***
# Architecture Reviewer

You use LSP-powered dependency and navigation skills to understand architecture...
```

This lets you compose: sub‑agent = persona + tools + LSP‑aware skills.

---

## 4. Hooks: Using LSP For Guardrails

Hooks in Claude Code are shell commands or prompts triggered by events such as `PreToolUse`, `PostToolUse`, `SubagentStop`, `SessionStart`, etc. [web:8][web:2] LSP supercharges hooks by letting them do **semantic** checks rather than only textual ones.

### 4.1 Where hooks live

- Project hooks: `.claude/hooks/hooks.json`. [web:8]
- Plugin hooks: `hooks/hooks.json` in plugin root or inline in `plugin.json`. [web:2][web:4]


### 4.2 Pattern: Pre‑edit impact warning

Goal: warn when editing a highly referenced symbol.

**hooks.json**:

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

**lsp-reference-impact.py** (conceptual skeleton):

```python
#!/usr/bin/env python3
import json
import sys
import subprocess

def extract_candidate_symbols(tool_input: dict) -> list[str]:
    # Placeholder: parse tool_input["file_content"] or diff to find changed names.
    return []

def main():
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")
    content = data.get("tool_input", {}).get("file_content", "")

    symbols = extract_candidate_symbols({"file_path": file_path, "content": content})
    high_impact = []

    for sym in symbols:
        # Call your LSP client wrapper (name illustrative)
        proc = subprocess.run(
            ["lsp-client", "findReferences", file_path, sym],
            capture_output=True,
            text=True
        )
        if proc.returncode != 0:
            continue
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        count = len(lines)
        if count > 20:
            high_impact.append((sym, count))

    if high_impact:
        print("⚠️ High-impact changes detected (LSP find-references):")
        for sym, cnt in sorted(high_impact, key=lambda x: -x):

![LSP Integration Strategy Flowchart](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/0d0e31f9b2505bc19b7edc5f1dfe21b3/5f7ea0f0-ea61-498e-aaa2-d810f9943dfa/eeebff9f.png)

LSP Integration Strategy Flowchart

print(f"  -  {sym}: {cnt} references")
        # Optionally return non-zero to block, or zero to just warn.
    else:
        print("✓ No high-impact symbols detected")

if __name__ == "__main__":
    main()
```

This hook encourages LSP‑driven impact checking before risky edits.

### 4.3 Pattern: Post‑edit type validation

Goal: after a write, run LSP to look for obvious type issues.

**hooks.json**:

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
    ]
  }
}
```

**lsp-type-check.py**:

```python
#!/usr/bin/env python3
import json
import sys
import subprocess

def main():
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")

    # Call language-specific LSP diagnostics or type check.
    # For example, if using pyright:
    proc = subprocess.run(
        ["pyright", "--outputjson", file_path],
        capture_output=True,
        text=True
    )
    if proc.returncode not in (0, 1):  # pyright uses 1 for type errors
        print(f"LSP type check failed unexpectedly:\n{proc.stderr}", file=sys.stderr)
        return

    try:
        result = json.loads(proc.stdout)
    except Exception:
        print("Could not parse pyright JSON output", file=sys.stderr)
        return

    diagnostics = result.get("generalDiagnostics", [])
    if not diagnostics:
        print("✓ LSP type check passed")
        return

    print("⚠️ LSP type check found issues:")
    for d in diagnostics[:20]:
        file = d.get("file", file_path)
        msg = d.get("message", "")
        sev = d.get("severity", "warning")
        line = d.get("range", {}).get("start", {}).get("line", "?")
        print(f"  [{sev}] {file}:{line} - {msg}")

if __name__ == "__main__":
    main()
```

This uses the language server’s own diagnostics to catch type problems introduced by edits.

### 4.4 Pattern: SessionStart LSP readiness check

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash -lc 'echo \"Checking LSP servers...\"; which pyright typescript-language-server gopls rust-analyzer 2>/dev/null || echo \"Some LSP servers not installed\"'"
          }
        ]
      }
    ]
  }
}
```

This makes LSP misconfiguration visible early in each session.

### 4.5 Pattern: SubagentStop metrics logging

You can log which sub‑agent ran and whether it succeeded, then use that data to improve skills later. [web:8][web:18][web:39]

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/log-subagent-run.py"
          }
        ]
      }
    ]
  }
}
```

Where `log-subagent-run.py` appends to a `lsp-metrics.jsonl` file with fields like `subagent`, `lsp_features_used`, `success`, etc.

---

## 5. Skills: Reusable LSP Patterns

Skills in Claude Code are model‑invoked prompt templates with optional scripts and tools. [web:6][web:35] They’re ideal for bundling complex LSP usage patterns so Claude can automatically apply them when your request matches the description.

### 5.1 How skills work (brief recap)

- Each Skill lives in `~/.claude/skills/<name>/SKILL.md` or in `.claude/skills/` inside a repo or plugin. [web:6][web:4]
- `SKILL.md` has YAML frontmatter with `name` and `description`, then instructions. [web:6][web:35]
- Claude loads only name + description at startup and pulls in full content only when needed (progressive disclosure). [web:6][web:35]
- Skills are **model‑invoked**: Claude chooses to use them when the description semantically matches the user’s request. [web:6]


### 5.2 Skill: LSP symbol navigation

**File:** `.claude/skills/lsp-symbol-navigation/SKILL.md`

```markdown
***
name: lsp-symbol-navigation
description: >
  Navigates code using Language Server Protocol (LSP). Uses go-to-definition to
  find symbol definitions, find-references to list usages, and hover to read
  type information. Use this Skill when the user asks where something is
  defined, how it is used, or how pieces of code are connected.
allowed-tools: Read, Bash, Grep
***

# LSP Symbol Navigation Skill

## When to use this Skill

Trigger this Skill when the user asks questions like:

- “Where is this function/class defined?”
- “What code calls this function?”
- “How is this type used across the project?”
- “Can you trace this flow from entry point to handler?”

## Core LSP operations

- **go-to-definition**: Resolve a symbol to its definition.
- **find-references**: Enumerate all usages of a symbol.
- **hover**: Fetch type signatures and documentation for symbols.

## Navigation process

Given a symbol (name + optional file/context):

1. Use go-to-definition to find the canonical definition.
2. Use hover on the definition to extract:
   - Signature (parameters, generics, return type).
   - Documentation summary.
3. Use find-references to list all usages.
4. Group usages by:
   - File/module.
   - Usage kind (call, import, implementation, test).
5. Present:
   - Definition location + snippet.
   - Type signature.
   - Reference counts and groupings.
   - Any suspicious usages or anomalies.

## Output format

When returning results, use a clear structure like:

- Definition: `path/to/file.ext:LINE`
- Signature: (from hover)
- Total references: N
- References:
  - `file1.ext:line` – [usage kind, short context]
  - `file2.ext:line` – [usage kind, short context]
```


### 5.3 Skill: LSP dependency analysis

```markdown
***
name: lsp-dependency-analysis
description: >
  Analyzes dependencies between modules and types using LSP. Uses find-references
  to see who depends on what and go-to-definition to trace dependency chains.
  Use this Skill for refactors, architecture reviews, and impact analysis.
allowed-tools: Read, Bash, Grep, Write
***

# LSP Dependency Analysis Skill

## When to use this Skill

Use when the user asks:

- “What depends on this module/type?”
- “Is this module tightly coupled?”
- “What breaks if I remove or change this type?”
- “Are there circular dependencies?”

## Steps

1. Identify target (module/file/type).
2. Use file reading to list its imports (direct dependencies).
3. Use go-to-definition to resolve imported symbols to their modules.
4. Use find-references on the target to find reverse dependencies:
   - Who imports or calls it.
5. Build:
   - Direct dependency list.
   - Reverse dependency list.
6. Detect patterns:
   - High coupling (many dependents).
   - Circular dependencies.
   - Orphaned modules.
7. Summarize risk and refactoring opportunities.
```


### 5.4 Skill: LSP type safety check

```markdown
***
name: lsp-type-safety-check
description: >
  Verifies type safety of code changes using LSP hover and find-references.
  Use this Skill before merging or deploying changes to catch type mismatches
  in parameters, returns, and implementations.
allowed-tools: Read, Bash, Grep
***

# LSP Type Safety Check Skill

## When to use this Skill

Use when the user asks:

- “Is this change type-safe?”
- “Will this refactor break any call sites?”
- “Are my TypeScript types still valid after these changes?”

## Steps

1. For each changed function or method:
   - Use go-to-definition to find the declaration.
   - Use hover to read parameter and return types.
2. Use find-references to list all call sites.
3. For each call site:
   - Use hover on arguments and return usage.
   - Compare against the function’s signature.
4. Classify issues:
   - Critical (incompatible types, missing args).
   - Warning (implicit conversions, nullability risks).
   - Info (missing annotations, broad types).
5. Produce a structured report and recommended fixes.
```


### 5.5 Progressive disclosure and scripts

Per best practices, each skill can ship with:

- `reference.md`: deeper LSP patterns and examples.
- `examples.md`: annotated example sessions.
- `scripts/`: small utilities like `type-check.py`, `analyze-deps.py`. [web:6][web:35]

The SKILL.md should reference these files (“See reference.md for advanced usage patterns”) so Claude can pull them in as needed without polluting baseline context.

---

## 6. Repository Structure To Maximize LSP

### 6.1 Core layout

```text
my-project/
├── .lsp.json                # LSP config for languages
├── .claude/
│   ├── CLAUDE.md            # Project instructions
│   ├── agents/
│   │   ├── lsp-navigator/
│   │   │   └── AGENT.md
│   │   ├── dependency-analyzer/
│   │   │   └── AGENT.md
│   │   └── type-checker/
│   │       └── AGENT.md
│   ├── skills/
│   │   ├── lsp-symbol-navigation/
│   │   │   └── SKILL.md
│   │   ├── lsp-dependency-analysis/
│   │   │   ├── SKILL.md
│   │   │   └── reference.md
│   │   └── lsp-type-safety-check/
│   │       └── SKILL.md
│   └── hooks/
│       ├── hooks.json
│       ├── lsp-type-check.py
│       └── lsp-reference-impact.py
└── src/ ...
```

This mirrors how plugins structure components (`agents/`, `skills/`, `hooks/`, `.lsp.json`). [web:4][web:2]

### 6.2 CLAUDE.md guidance

**File:** `.claude/CLAUDE.md` [web:6][web:9]

```markdown
# Project Guidance (LSP Enabled)

This project uses Language Server Protocol (LSP) for semantic code navigation.

## LSP Usage

- Prefer LSP **go-to-definition** over raw file search.
- Use **find-references** before refactoring any widely used symbol.
- Use **hover** to verify types and signatures instead of guessing.

## Subagents

- `lsp-navigator` for code navigation and exploration.
- `dependency-analyzer` for coupling and impact analysis.
- `type-checker` for type safety review.

## Skills

- `lsp-symbol-navigation`: Navigate symbols and usages.
- `lsp-dependency-analysis`: Analyze module dependencies.
- `lsp-type-safety-check`: Verify type safety before merge/deploy.

When in doubt, ask Claude to “use LSP to…” rather than “search the codebase for…”.
```

This sets project‑wide defaults and hints. [web:6]

---

## 7. Designing Self‑Improving LSP Skills

Native docs emphasize that skills are model‑invoked and can be combined with hooks and tools. [web:6][web:33][web:39] To make them **self‑improving**:

1. **Collect metrics**: Which skills run, which LSP operations used, success/failure.
2. **Analyze patterns**: Where did the skill fail? Which LSP features helped most? [web:18][web:39]
3. **Update skill instructions**: Add heuristics for ambiguous cases, improve descriptions, add examples.
4. **Version skills**: Track changes and reasons in frontmatter or comments. [web:35]

### 7.1 Metrics collector skeleton

```python
#!/usr/bin/env python3
# .claude/skills/lsp-metrics/collector.py

import json
from pathlib import Path
from datetime import datetime
import sys

LOG_PATH = Path.home() / ".claude" / "lsp-metrics.jsonl"

def log_metric(event: dict):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    event["timestamp"] = datetime.utcnow().isoformat()
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(event) + "\n")

def main():
    data = json.load(sys.stdin)
    # data could include subagent name, tool used, etc.
    event = {
        "subagent": data.get("subagent_name"),
        "skill": data.get("skill_name"),
        "lsp_features": data.get("lsp_features", []),
        "success": data.get("success", True),
    }
    log_metric(event)

if __name__ == "__main__":
    main()
```

Trigger this from `SubagentStop` or `PostToolUse` hooks.

### 7.2 Improvement loop

Once a week, run a script that:

- Parses `lsp-metrics.jsonl`.
- Aggregates by `skill` and `lsp_features`.
- Identifies low success‑rate combinations.
- Emits suggestions like “when using find‑references alone, failure rate is high; combine with go‑to-definition and hover to disambiguate”.

Then you update each relevant SKILL.md with:

- “If find‑references returns too many candidate symbols, first use go‑to-definition on the symbol in the primary file to confirm identity before inspecting references.”

Over time, your LSP skills encode more robust heuristics derived from real usage, not just initial guesses.

---

## 8. Common Pitfalls \& How To Avoid Them

| Pitfall | Cause | Mitigation |
| :-- | :-- | :-- |
| Still prompting as if no LSP | Old habits (“grep here”) | Adopt symbol‑centric prompts; mention LSP operations explicitly |
| Overloading one agent | One “mega” agent for everything | Create focused sub‑agents per LSP task |
| Hooks blocking too early | Heavy PreToolUse checks | Favor PostToolUse/commit‑time checks for expensive operations [web:18] |
| Skills not triggering | Vague descriptions | Use concrete capability + trigger phrasing in `description` [web:6] |
| LSP flaky or slow | Misconfigured server / too many calls | Fix `.lsp.json`, cache results, narrow queries |
| Confusing similar symbols | Multiple functions/classes with same name | Combine go‑to-definition + hover to disambiguate before reading references |
| Missing languages | `.lsp.json` incomplete | Incrementally add language servers as needed |


---

## 9. Phased Adoption Plan (Recap)

1. **Phase 1: Enable LSP**
    - Install language servers (Pyright, TS server, etc.).
    - Create `.lsp.json`.
    - Add CLAUDE.md with high‑level LSP guidance.
2. **Phase 2: Sub‑agents**
    - Implement `lsp-navigator`, `dependency-analyzer`, `type-checker`.
    - Test them on real tasks.
3. **Phase 3: Skills**
    - Add three core skills (symbol navigation, dependency analysis, type safety).
    - Use progressive disclosure and external reference files.
4. **Phase 4: Hooks**
    - Add PreToolUse impact warnings.
    - Add PostToolUse type checks.
    - Optionally add SessionStart and SubagentStop hooks.
5. **Phase 5: Self‑Improvement**
    - Log metrics.
    - Weekly analysis to refine skills.
    - Version and document improvements.

---

## 10. Summary

LSP turns Claude Code from a “smart grep” into something much closer to an IDE‑style assistant:

- Prompting should explicitly reference **LSP operations** and **symbol‑based reasoning**.
- Sub‑agents should be **specialists** for navigation, dependency analysis, and type checking.
- Hooks should enforce **semantic guardrails** rather than just textual checks.
- Skills should encapsulate **LSP usage patterns** with progressive disclosure and scripts.
- Repository structure should centralize `.lsp.json`, agents, skills, and hooks so teams share one configuration.
- Self‑improving skills require modest **metrics collection** and a regular review cadence, but quickly pay off in more reliable behavior.

You can paste the sections above into `docs/lsp_research_findings.md` or split them across multiple files (agents, skills, hooks) exactly as written.

```
<span style="display:none">[^1][^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^2][^20][^21][^22][^23][^24][^25][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://code.claude.com/docs/en/sub-agents
[^2]: https://code.claude.com/docs/en/skills
[^3]: https://code.claude.com/docs/en/hooks-guide
[^4]: https://code.claude.com/docs/en/plugins-reference
[^5]: https://code.claude.com/docs/en/plugins
[^6]: https://code.claude.com/docs/en/common-workflows
[^7]: https://code.claude.com/docs/en/mcp
[^8]: https://www.reddit.com/r/ClaudeAI/comments/1otdfo9/lsp_is_coming_to_claude_code_and_you_can_try_it/
[^9]: https://www.youtube.com/watch?v=cPTEal0ILDI
[^10]: https://www.youtube.com/watch?v=lffYEu5MhSQ
[^11]: https://www.linkedin.com/pulse/claude-code-now-has-lsp-support-heres-why-actually-matters-harwood-h27hc
[^12]: https://www.aifreeapi.com/en/posts/claude-code-lsp
[^13]: https://www.linkedin.com/pulse/claude-platform-skills-plugins-subagents-tools-hooks-charles-guo-302yc
[^14]: https://www.reddit.com/r/ClaudeCode/comments/1pyjl4r/skills_agents_plugins/
[^15]: https://spec-weave.com/docs/glossary/terms/lsp/
[^16]: https://www.youngleaders.tech/p/claude-skills-commands-subagents-plugins
[^17]: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
[^18]: https://github.com/ktnyt/cclsp
[^19]: https://github.com/ChrisWiles/claude-code-showcase
[^20]: https://x.com/akiojin/status/2002316767310274871
[^21]: https://blog.sshh.io/p/how-i-use-every-claude-code-feature
[^22]: https://sankalp.bearblog.dev/my-experience-with-claude-code-20-and-how-to-get-better-at-using-coding-agents/
[^23]: https://github.com/anthropics/claude-code/issues/5495
[^24]: https://github.com/hesreallyhim/awesome-claude-code
[^25]: https://www.reddit.com/r/ClaudeCode/comments/1msfyrm/i_built_a_tool_to_get_realtime_lsp_diagnostics/```

