# Publishing Weave CLI to PyPI

Guide for publishing Weave to PyPI so users can install with `pip install weave-cli`.

## Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Verify email address

2. **API Token**
   - Go to https://pypi.org/manage/account/token/
   - Create API token for "Entire account" or "weave-cli" project
   - Save token securely

3. **Install Build Tools**
   ```bash
   pip install --upgrade build twine
   ```

## Build Package

### 1. Clean Previous Builds

```bash
# Remove old builds
rm -rf dist/ build/ *.egg-info

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name '*.pyc' -delete
```

### 2. Update Version

Edit `pyproject.toml`:

```toml
[project]
name = "weave-cli"
version = "0.1.0"  # Update this version
```

### 3. Build Distribution

```bash
# Build wheel and source distribution
python -m build

# Output:
# dist/
#   weave_cli-0.1.0-py3-none-any.whl
#   weave-cli-0.1.0.tar.gz
```

### 4. Check Package

```bash
# Check package metadata
twine check dist/*

# Should output:
# Checking dist/weave_cli-0.1.0-py3-none-any.whl: PASSED
# Checking dist/weave-cli-0.1.0.tar.gz: PASSED
```

## Test Installation

Before publishing, test installation locally:

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate

# Install from wheel
pip install dist/weave_cli-0.1.0-py3-none-any.whl

# Test
weave --version
weave --help

# Deactivate
deactivate
rm -rf test-env
```

## Publish to TestPyPI (Optional)

Test the publishing process first:

### 1. Create TestPyPI Account

- Register at https://test.pypi.org/account/register/
- Create API token

### 2. Upload to TestPyPI

```bash
# Upload
twine upload --repository testpypi dist/*

# Enter your TestPyPI token when prompted
```

### 3. Test Install from TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ weave-cli
```

## Publish to PyPI

### Using API Token (Recommended)

```bash
# Set token as environment variable
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your-api-token>

# Upload to PyPI
twine upload dist/*
```

### Interactive Upload

```bash
# Upload with prompts
twine upload dist/*

# Enter credentials:
# Username: __token__
# Password: <your-api-token>
```

## Post-Publishing

### 1. Verify on PyPI

Visit https://pypi.org/project/weave-cli/ to confirm:
- Package metadata is correct
- README renders properly
- All classifiers are shown
- Download links work

### 2. Test Installation

```bash
# Install from PyPI
pip install weave-cli

# Test basic functionality
weave --version
weave setup
```

### 3. Tag Release in Git

```bash
# Create git tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

### 4. Create GitHub Release

1. Go to https://github.com/weave/weave-cli/releases/new
2. Select tag: `v0.1.0`
3. Release title: `v0.1.0`
4. Description: Copy from CHANGELOG or deployment summary
5. Attach built distributions (wheel and tar.gz)
6. Publish release

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Check package
      run: twine check dist/*

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add secret to GitHub:
1. Settings → Secrets and variables → Actions
2. New repository secret: `PYPI_API_TOKEN`
3. Value: Your PyPI API token

## Version Management

### Semantic Versioning

Follow semver (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Examples:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.0` → `0.2.0`: New feature
- `0.9.0` → `1.0.0`: Stable release

### Update Version

Edit `pyproject.toml`:

```toml
version = "0.2.0"
```

Or use bump2version:

```bash
pip install bump2version

# Bump patch: 0.1.0 → 0.1.1
bump2version patch

# Bump minor: 0.1.0 → 0.2.0
bump2version minor

# Bump major: 0.1.0 → 1.0.0
bump2version major
```

## Troubleshooting

### "File already exists"

```bash
# Error: File already exists on PyPI

# Solution: Increment version number
# You cannot re-upload the same version
```

### "Invalid package name"

```bash
# Package name must use hyphens, not underscores
# Use: weave-cli
# Not: weave_cli
```

### "README not rendering"

```bash
# Ensure README.md is specified in pyproject.toml
[project]
readme = "README.md"

# Check with:
twine check dist/*
```

### "Missing dependencies"

```bash
# Check all dependencies are listed
[project]
dependencies = [
    "typer>=0.9.0",
    "rich>=13.7.0",
    # ...
]
```

## Checklist

Before publishing:

- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG.md updated with changes
- [ ] All tests passing (`pytest`)
- [ ] README.md is up to date
- [ ] LICENSE file exists
- [ ] Build artifacts clean (`rm -rf dist/`)
- [ ] Package builds successfully (`python -m build`)
- [ ] Package checks pass (`twine check dist/*`)
- [ ] Local install test works
- [ ] TestPyPI upload works (optional)
- [ ] Git tag created
- [ ] GitHub release created

## Resources

- **PyPI**: https://pypi.org/
- **TestPyPI**: https://test.pypi.org/
- **Packaging Guide**: https://packaging.python.org/
- **Twine Docs**: https://twine.readthedocs.io/
- **Build Docs**: https://pypa-build.readthedocs.io/

## First-Time Publishing

For initial PyPI submission:

1. Ensure package name "weave-cli" is available
2. Check similar names don't exist
3. Verify you own domain if using custom URLs
4. Start with version 0.1.0 for beta
5. Consider TestPyPI first
6. Get feedback before 1.0.0 release

## Updating After Publishing

Users can update with:

```bash
# Upgrade to latest
pip install --upgrade weave-cli

# Install specific version
pip install weave-cli==0.2.0

# Install pre-release
pip install --pre weave-cli
```
