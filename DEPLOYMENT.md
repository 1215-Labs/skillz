# LSP Integration Deployment Package

## 🚀 Quick Start

### 1. Automated Setup
```bash
python setup_lsp.py
```

### 2. Manual Setup
```bash
# Install Python LSP
pip install pyright  # or: uv tool install pyright

# Install TypeScript LSP  
npm install -g typescript-language-server

# Set environment variable
export ENABLE_LSP_TOOL=1

# Copy configuration files
cp .lsp.json .claude/ YOUR_PROJECT_ROOT/
```

## 📁 Files to Copy

Copy these files/directories to your target project:

```
your-project/
├── .lsp.json                    # LSP server configuration
└── .claude/
    ├── CLAUDE.md                  # LSP usage guidance
    ├── agents/                    # LSP-aware sub-agents
    ├── skills/                    # Reusable LSP patterns  
    └── hooks/                     # Automated checks
```

## 🧪 Testing LSP Integration

Create a test file and try these commands:

```python
# test.py
def calculate_sum(a: int, b: int) -> int:
    return a + b

result = calculate_sum(5, 3)
```

Then in Claude Code:
- "Use LSP go-to-definition on `calculate_sum`"
- "Use LSP hover on `result`"  
- "Use LSP find-references for `calculate_sum`"

## 🎯 Common Workflows

### Navigation
"Use LSP to show me the definition of `User` class and all its references"

### Impact Analysis  
"Before renaming `authenticate` method, use LSP find-references to show all call sites"

### Type Safety
"Verify these changes are type-safe using LSP hover and references"

## 🔧 Environment Variables

```bash
export ENABLE_LSP_TOOL=1  # Enable LSP in Claude Code
```

Add this to your shell profile (~/.bashrc, ~/.zshrc) for persistence.