# Virtual Environment Setup Guide - Python 3.11

This guide will help you set up a Python 3.11 virtual environment for the Federated Learning CKD project.

---

## Prerequisites

Ensure Python 3.11 is installed on your system:

```bash
python3.11 --version
```

If not installed, download from: https://www.python.org/downloads/

---

## Setup Instructions

### 1. Navigate to Project Directory

```bash
cd /path/to/Major-Project-PE-FL-DP-CKD-main
```

### 2. Create Virtual Environment with Python 3.11

```bash
python3.11 -m venv venv
```

This creates a `venv` directory containing the isolated Python 3.11 environment.

### 3. Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

After activation, your prompt should show `(venv)` prefix.

### 4. Verify Python Version

```bash
python --version
```

Should output: `Python 3.11.x`

### 5. Upgrade pip

```bash
pip install --upgrade pip
```

### 6. Install Project Dependencies

**For the main FL-DP-Healthcare module:**
```bash
cd FL-DP-Healthcare
pip install -r requirements.txt
```

**For the web application:**
```bash
cd App
pip install -r requirements.txt
```

### 7. Verify Installation

```bash
python -c "import torch, numpy, pandas, sklearn, matplotlib; print('✅ Environment ready!')"
```

---

## Deactivate Virtual Environment

When you're done working:

```bash
deactivate
```

---

## Troubleshooting

### Issue: `python3.11: command not found`

**Solution:** Install Python 3.11 or create an alias:

```bash
# Linux/macOS
alias python3.11=/usr/bin/python3.11

# Or use the full path
/usr/local/bin/python3.11 -m venv venv
```

### Issue: Permission denied on activation (Windows PowerShell)

**Solution:** Enable script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Module not found after installation

**Solution:** Ensure virtual environment is activated and reinstall:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `python3.11 -m venv venv` | Create virtual environment |
| `source venv/bin/activate` | Activate (Linux/Mac) |
| `venv\Scripts\activate` | Activate (Windows) |
| `deactivate` | Deactivate environment |
| `pip list` | Show installed packages |
| `pip freeze > requirements.txt` | Export dependencies |
| `which python` | Show Python path (verify venv) |

---

## Best Practices

1. **Always activate** the virtual environment before working on the project
2. **Never commit** the `venv/` directory to version control (already in `.gitignore`)
3. **Update requirements.txt** when adding new dependencies:
   ```bash
   pip freeze > requirements.txt
   ```
4. **Use the same Python version** (3.11) across all team members for consistency

---

## Why Python 3.11?

- **Performance**: 10-60% faster than Python 3.10
- **Better error messages**: More helpful debugging information
- **Type hints improvements**: Enhanced static typing support
- **Compatibility**: Works with all project dependencies (PyTorch, FastAPI, etc.)

---

**Note:** This project specifically requires Python 3.11 for optimal performance and compatibility with the federated learning framework.