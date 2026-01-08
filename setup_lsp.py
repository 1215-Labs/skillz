#!/usr/bin/env python3
"""
LSP Integration Setup Script

This script installs and configures LSP servers for Claude Code integration.
Supports Python, TypeScript, JavaScript, and can be extended for other languages.
"""

import subprocess
import sys
import json
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_uv():
    """Check if UV package manager is available."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_python_lsp():
    """Install Python LSP server (pyright)."""
    if check_uv():
        return run_command(
            "uv tool install pyright",
            "Installing Pyright (Python LSP) with UV"
        )
    else:
        return run_command(
            "pip install pyright",
            "Installing Pyright (Python LSP) with pip"
        )


def install_typescript_lsp():
    """Install TypeScript/JavaScript LSP server."""
    return run_command(
        "npm install -g typescript-language-server",
        "Installing TypeScript Language Server"
    )


def create_lsp_config(target_dir):
    """Create .lsp.json configuration file."""
    config = {
        "python": {
            "command": "pyright",
            "args": ["--outputjson"],
            "extensionToLanguage": {".py": "python"}
        },
        "typescript": {
            "command": "typescript-language-server", 
            "args": ["--stdio"],
            "extensionToLanguage": {
                ".ts": "typescript",
                ".tsx": "typescript"
            }
        },
        "javascript": {
            "command": "typescript-language-server",
            "args": ["--stdio"], 
            "extensionToLanguage": {
                ".js": "javascript",
                ".jsx": "javascript"
            }
        }
    }
    
    lsp_file = Path(target_dir) / ".lsp.json"
    with open(lsp_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created {lsp_file}")


def setup_claude_directory(target_dir):
    """Set up Claude Code configuration directory structure."""
    claude_dir = Path(target_dir) / ".claude"
    
    # Create directory structure
    dirs_to_create = [
        claude_dir / "agents" / "lsp-navigator",
        claude_dir / "agents" / "dependency-analyzer", 
        claude_dir / "agents" / "type-checker",
        claude_dir / "skills" / "lsp-symbol-navigation",
        claude_dir / "skills" / "lsp-dependency-analysis",
        claude_dir / "skills" / "lsp-type-safety-check",
        claude_dir / "hooks"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created Claude directory structure in {claude_dir}")


def setup_environment():
    """Set up environment variables for LSP."""
    print("🔧 Setting up environment variables...")
    
    # For current session
    os.environ["ENABLE_LSP_TOOL"] = "1"
    
    # Add to shell profile for persistence
    shell_profiles = ["~/.bashrc", "~/.zshrc", "~/.profile"]
    added = False
    
    for profile in shell_profiles:
        profile_path = Path(profile).expanduser()
        if profile_path.exists():
            with open(profile_path, 'a') as f:
                f.write("\n# Claude Code LSP Support\nexport ENABLE_LSP_TOOL=1\n")
            print(f"✅ Added LSP environment variable to {profile}")
            added = True
            break
    
    if not added:
        print("⚠️  No shell profile found. Manually add: export ENABLE_LSP_TOOL=1")


def verify_installation():
    """Verify that LSP servers are properly installed."""
    print("\n🔍 Verifying LSP installation...")
    
    # Check pyright
    try:
        result = subprocess.run(["pyright", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ Pyright installed: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Pyright not found in PATH")
    
    # Check typescript-language-server
    try:
        result = subprocess.run(["typescript-language-server", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ TypeScript Language Server installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ TypeScript Language Server not found in PATH")


def main():
    """Main installation function."""
    print("🚀 Claude Code LSP Integration Setup")
    print("=" * 40)
    
    target_dir = os.getcwd()
    print(f"Target directory: {target_dir}")
    
    # Install LSP servers
    success = True
    success &= install_python_lsp()
    success &= install_typescript_lsp()
    
    if not success:
        print("\n❌ Some LSP servers failed to install. Check the errors above.")
        sys.exit(1)
    
    # Create configuration
    create_lsp_config(target_dir)
    setup_claude_directory(target_dir)
    setup_environment()
    verify_installation()
    
    print("\n🎉 LSP integration setup completed!")
    print("\n📚 Next steps:")
    print("1. Restart your terminal or run: export ENABLE_LSP_TOOL=1")
    print("2. Run: claude")
    print("3. Test with: 'Use LSP go-to-definition on a symbol'")
    print("\n📖 For detailed patterns, see: Docs/LSP-Research/lsp_implementation_quick_reference.md")


if __name__ == "__main__":
    main()