# Claude Code LSP Integration Configuration

This directory contains Claude Code configuration for LSP-aware development.

## 🚀 Quick LSP Commands

### Core Operations
- **go-to-definition**: "Jump to the definition of `symbol_name`"
- **find-references**: "Show all references to `symbol_name`"  
- **hover**: "Show type info for `symbol_name`"

### Example Workflows
```
"Use LSP to navigate from `UserService.authenticate` to all its callers"
"Before renaming User class, use LSP find-references to assess impact"
"Is this type-safe? Use LSP hover on function signatures to verify"
```

## 🤖 Available Agents

### LSP Navigator
Use for: Code navigation, understanding unfamiliar code
```
"Use LSP Navigator to trace how authentication flows through the system"
```

### Dependency Analyzer  
Use for: Impact analysis, architecture reviews
```
"Use Dependency Analyzer to see what depends on the User type"
```

### Type Checker
Use for: Safety verification before changes
```
"Use Type Checker to verify these changes won't break existing code"
```

## 🛠️ Skills

### Symbol Navigation
- Find definitions, references, and usage patterns
- Works across multiple languages (Python, TypeScript, etc.)

### Dependency Analysis  
- Map inbound/outbound dependencies
- Identify coupling and impact zones

### Type Safety Check
- Verify type contracts before deployment
- Catch parameter/return type mismatches

## 🔧 Hooks Configuration

**Post-edit validation**: Automatic type checking after edits
**Pre-edit warnings**: Impact analysis for high-risk changes
**Session start**: Verify LSP servers are running

## 📁 Directory Structure

```
.claude/
├── CLAUDE.md              # This file - usage guidance
├── agents/                 # Specialized LSP agents
├── skills/                 # Reusable LSP patterns  
└── hooks/                  # Automated LSP checks
```

## 🎯 Best Practices

1. **Prefer semantic operations**: Use LSP instead of text search
2. **Ask for impact analysis**: Before refactoring, check references
3. **Verify type safety**: Use hover before committing changes
4. **Leverage automation**: Hooks provide continuous safety checks

## 📚 Reference Documentation

See `../Docs/LSP-Research/lsp_implementation_quick_reference.md` for detailed patterns and examples.
