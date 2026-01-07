<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Expand the methodology section with step by step procedures

Below is an expanded methodology section you can drop into the research doc, with explicit step‑by‑step procedures.

```markdown
## 7. Research Methodology (Expanded, Step‑by‑Step)

This section describes, in concrete steps, how to research, design, and iterate on LSP integration with Claude Code in a real project.

---

### 7.1 Phase 1 – Understand Current Capabilities

**Goal:** Get a precise picture of what Claude Code + LSP can do in your environment.

**Steps:**

1. **Read official docs**
   - Open:
     - Sub‑agents docs. [web:7]
     - Skills docs. [web:6]
     - Hooks guide. [web:8]
     - Plugins / plugins‑reference docs. [web:2][web:4]
     - LSP‑specific blog/posts or guides. [web:12][web:31][web:32]
   - Note:
     - Where `.lsp.json` is expected.
     - How agents, skills, hooks, plugins are discovered.
     - Any examples of LSP or code‑intelligence tools being used.

2. **Inventory your languages and tools**
   - List languages in your repo (e.g. TypeScript, Python, Go, Rust).
   - For each language, check if a well‑supported LSP server exists (Pyright, typescript‑language‑server, gopls, rust‑analyzer, etc.). [web:12][web:17]
   - Decide which languages to enable first (start with 1–2).

3. **Install language servers**
   - Install and confirm each server runs on the command line:
     - `pyright --help` for Python.
     - `typescript-language-server --help` for TS/JS.
     - `gopls version` for Go.
     - `rust-analyzer --version` for Rust. [web:12][web:31]
   - Record installation commands in `docs/lsp-setup-guide.md` or CLAUDE.md.

4. **Configure `.lsp.json`**
   - At the repo or plugin root, create `.lsp.json` with one language to start (e.g. Python).
   - Add basic `command`, minimal `args`, and `extensionToLanguage` mapping.
   - Verify syntax (valid JSON, no trailing commas).

5. **Smoke‑test LSP in Claude Code**
   - Start Claude Code on the repo.
   - Ask a simple navigation question:
     - “Use LSP to go to the definition of `some_function` in `path/to/file.py`.”
   - Confirm that:
     - It resolves the correct location.
     - It no longer relies purely on grep/file scans.
   - Adjust `.lsp.json` if needed.

---

### 7.2 Phase 2 – Analyze Current Workflows

**Goal:** Identify where LSP will provide the most value in your existing Claude Code usage.

**Steps:**

1. **Collect typical tasks**
   - Look at:
     - Recent conversations with Claude Code.
     - Common commands developers type (“where is X”, “what uses Y”, “is this safe to change?”).
     - Manual IDE actions devs perform (go‑to‑definition in editor, grep for symbol, etc.). [web:18][web:39]

2. **Classify tasks by intent**
   - Tag each task as:
     - *Navigation*: find definitions/usages.
     - *Refactor / impact*: what breaks if we change X?
     - *Type safety*: are these changes type‑correct?
     - *Architecture*: how are modules connected?

3. **Map tasks to LSP features**
   - For each class:
     - Navigation → go‑to‑definition + find‑references.
     - Impact → find‑references + hover.
     - Type safety → hover + diagnostics.
     - Architecture → find‑references + documentSymbol (if available).

4. **Prioritize problem areas**
   - Pick tasks where:
     - Developers currently spend a lot of time.
     - Errors often slip through (e.g. refactors).
     - Plain text search is clearly insufficient.

5. **Decide on first LSP workflows**
   - Choose 2–3 high‑impact workflows to target first, such as:
     - “Understand this function’s definition and usages.”
     - “Refactor this type safely.”
     - “Check if code is type‑safe before deploy.”

---

### 7.3 Phase 3 – Design LSP‑Aware Prompts & Agents

**Goal:** Translate prioritized workflows into concrete prompts and sub‑agent designs.

**Steps:**

1. **Draft LSP‑aware prompt templates**
   - For each prioritized workflow, write a prompt that explicitly:
     - Names the LSP operations (go‑to‑definition, find‑references, hover).
     - Specifies the order they should be used.
     - Specifies expected outputs (definition, references, type info, risk summary).

2. **Create sub‑agent specifications**
   - For each workflow category, define:
     - Agent name (e.g. `lsp-navigator`, `dependency-analyzer`, `type-checker`).
     - One‑sentence description explicitly mentioning LSP.
     - Tools required (Read, Bash, Grep, etc.). [web:7]
     - Model (inherit or a specific model).
   - Write an AGENT.md with:
     - A “Capabilities” section listing LSP operations.
     - A “Process” section describing step‑by‑step behavior.
     - A “Output format” section for consistent responses.

3. **Align with Skills**
   - Identify which behaviors should be **agent‑internal** vs **skill‑based**:
     - Stable, reusable patterns → Skills. [web:6][web:35]
     - Persona and role framing → Sub‑agent AGENT.md.
   - Plan Skills such as `lsp-symbol-navigation`, `lsp-dependency-analysis`, `lsp-type-safety-check` aligned with agent responsibilities.

4. **Review with team**
   - Share draft prompts and AGENT.md definitions with 1–2 developers.
   - Ask: “Does this match how you think about navigation / refactors / type safety?”
   - Incorporate feedback, especially about terminology and naming.

---

### 7.4 Phase 4 – Implement Skills and Hooks

**Goal:** Encode LSP patterns into Skills and add hooks for automated checks.

**Steps:**

1. **Implement Skills**
   - For each planned Skill:
     - Create directory `.claude/skills/<skill-name>/`.
     - Add `SKILL.md` with:
       - Minimal frontmatter (`name`, `description`, `allowed-tools`). [web:6]
       - “When to use” section (scenarios).
       - “Process” section with concrete LSP steps.
       - “Output format” section.
   - Keep SKILL.md concise; move deep details into `reference.md` or `examples.md` alongside.

2. **Add utility scripts (optional but recommended)**
   - For Skills that need repeated shell/tools logic, add:
     - `.claude/skills/<skill-name>/scripts/*.py` or `.sh`.
   - Reference them conceptually in SKILL.md (“run the `type-check.py` script when needed”).

3. **Design hook behaviors**
   - Decide:
     - Which LSP checks run *before* edits (PreToolUse) vs *after* (PostToolUse).
     - What conditions are “warn only” vs “fail/build‑blocker”.
   - Examples:
     - PreToolUse: LSP reference count warning for high‑impact symbols.
     - PostToolUse: LSP type diagnostics on changed file(s). [web:8]

4. **Implement hooks.json**
   - Create `.claude/hooks/hooks.json`.
   - Add entries for:
     - `PreToolUse` with a command to warn on high‑reference changes.
     - `PostToolUse` with a command to run type diagnostics.
     - Optionally, `SessionStart` and `SubagentStop` hooks for readiness check and metrics logging.

5. **Wire hooks to LSP tools**
   - In hook scripts:
     - Shell out to language servers or an `lsp-client` wrapper.
     - Parse minimal JSON or textual output.
     - Print concise messages for Claude and developers.

---

### 7.5 Phase 5 – Test and Iterate

**Goal:** Validate that LSP‑aware workflows actually improve navigation, refactoring, and safety in your real repo.

**Steps:**

1. **Create test scenarios**
   - Identify a handful of realistic tasks:
     - “Find where this core function is defined and used.”
     - “Refactor this type and ensure no breakages.”
     - “Check type safety after changing these files.”

2. **Run with and without LSP**
   - For each scenario:
     - Run it using old, non‑LSP prompts (“search for X”, etc.).
     - Run it using new, LSP‑aware prompts and agents.
   - Measure:
     - Steps or time to completion.
     - Number of errors discovered or missed.
     - Subjective developer satisfaction.

3. **Observe failure modes**
   - Note when:
     - LSP cannot resolve a symbol (missing server, incomplete config).
     - Too many references are returned (ambiguous symbol names).
     - Hover lacks useful type info (poor type annotations).
   - Record concrete examples (file, symbol, what went wrong).

4. **Refine prompts, skills, and hooks**
   - Update SKILL.md and AGENT.md to address failure modes:
     - Add fallback logic (e.g., combine go‑to‑definition + hover to disambiguate).
     - Add instructions like “If find‑references returns too many results, filter by file path or symbol kind.”
   - Adjust hooks to reduce noise:
     - Tune thresholds (e.g., warn only if references > N).
     - Limit diagnostics to changed files.

5. **Re‑test after adjustments**
   - Re‑run the same scenarios with updated configuration.
   - Confirm that:
     - Errors are fewer.
     - Responses are more focused.
     - Hooks produce fewer false positives.

---

### 7.6 Phase 6 – Instrumentation & Self‑Improvement

**Goal:** Build a continuous improvement loop for LSP‑based skills and agents.

**Steps:**

1. **Define metrics**
   - Decide what to log for each LSP‑heavy operation:
     - `skill_name` and/or `subagent_name`.
     - `lsp_features_used` (e.g. `["goToDefinition","findReferences"]`).
     - `task_type` (navigation, refactor, type check).
     - `success` boolean (or rating if you ask devs to tag outcomes).
     - Optional: number of references, time taken.

2. **Implement logging**
   - Add a hook (`SubagentStop` or `PostToolUse`) that calls a metrics script.
   - Script appends JSON lines to a log file (e.g. `~/.claude/lsp-metrics.jsonl`):
     - One line per sub‑agent/skill execution.
   - Keep the format simple and stable.

3. **Schedule regular analysis**
   - Weekly or bi‑weekly, run a small analysis script that:
     - Groups metrics by `skill` and `lsp_features`.
     - Computes success rates and approximate usage frequencies.
     - Identifies:
       - Low‑success combinations to improve.
       - High‑success combinations to expand.

4. **Generate improvement suggestions**
   - From analysis, produce a short markdown report:
     - “Skill X often fails when using find‑references alone. Suggest combining it with go‑to‑definition first.”
     - “Skill Y performs best when hover is used on all parameters before checking references.”
   - Store this in `docs/lsp-improvement-log.md` or under `.claude/skills/lsp-metrics/`.

5. **Update skills and agents**
   - Revise SKILL.md and AGENT.md based on suggestions:
     - Clarify instructions.
     - Add decision rules (“if ambiguous, then …”).
     - Add new example usages.

6. **Version changes**
   - Add a simple `version:` field or changelog comment to SKILL.md:
     - `version: 1.1` → “Added disambiguation step when find‑references returns many results.”
   - Commit changes to version control with meaningful messages.

7. **Repeat**
   - Continue the cycle:
     - Instrument → Analyze → Improve → Version → Deploy.
   - Over time, LSP‑based skills become more aligned with your repo and team habits.

---

### 7.7 Phase 7 – Share & Standardize

**Goal:** Make LSP best practices reusable across projects and team members.

**Steps:**

1. **Extract generic components**
   - Identify skills/agents/hooks that are not repo‑specific (e.g. generic Python type checker, generic TS navigator).
   - Move them into:
     - A dedicated plugin repository, or
     - A `templates/` directory.

2. **Wrap as a plugin (optional)**
   - Use Claude Code plugin structure: `agents/`, `skills/`, `hooks/`, `.lsp.json`, `plugin.json`. [web:4][web:2]
   - Publish internally (Git, marketplace) so other repos can reuse.

3. **Document standards**
   - In an internal doc, define:
     - Where `.lsp.json` should live.
     - Baseline set of LSP‑aware agents and skills required for new repos.
     - Recommended hooks for PreToolUse/PostToolUse.

4. **Onboard new projects**
   - For each new repo:
     - Copy the standard `.claude/` scaffold.
     - Adjust `.lsp.json` for languages present.
     - Tune prompts minimally for domain specifics.

5. **Onboard new team members**
   - Provide a short “Using LSP with Claude Code” guide:
     - Show how to ask LSP‑aware questions.
     - Introduce sub‑agents and skills.
     - Show examples of safe refactors with find‑references + hover.

6. **Audit periodically**
   - Quarterly, review:
     - Are there new languages or frameworks needing LSP?
     - Are hooks too noisy or too quiet?
     - Are skills still aligned with how the team actually works?

This closes the loop from initial research to an evolving, organization‑wide practice.
```

If you’d like, the next step can be to tailor this methodology to your specific repo (languages, size, and current Claude Code setup) so the phases map directly onto a concrete implementation plan.

