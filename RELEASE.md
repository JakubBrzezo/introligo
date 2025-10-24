# Release Process

This document describes the automated release process for Introligo to PyPI.

## Overview

Introligo uses an automated CI/CD pipeline that:
- Automatically extracts version from git tags
- Builds distribution packages
- Publishes to PyPI using trusted publishing
- Creates GitHub releases
- Tests the installation across multiple Python versions

## Prerequisites

### 1. PyPI Trusted Publishing Setup

Configure PyPI trusted publishing (one-time setup):

**IMPORTANT**: Since the `introligo` package already exists on PyPI, you must configure the trusted publisher on the **existing project**, not as a "pending publisher":

1. **Log in to PyPI**: https://pypi.org/
2. **Go to project publishing settings**: https://pypi.org/manage/project/introligo/settings/publishing/
3. **Click "Add a new publisher"** in the "Publishing" section
4. **Fill in the trusted publisher configuration**:
   - **Owner**: `JakubBrzezo` (your GitHub username)
   - **Repository name**: `introligo`
   - **Workflow filename**: `publish-pypi.yml`
   - **Environment name**: `pypi`
5. **Save the configuration**

**Note for new projects**: If the package doesn't exist on PyPI yet, use [PyPI Pending Publishers](https://pypi.org/manage/account/publishing/) instead.

This allows GitHub Actions to publish without needing API tokens.

### 2. GitHub Repository Setup

No secrets needed! Trusted publishing uses OIDC tokens automatically.

## How to Release

### Step 1: Update CHANGELOG.md

Before creating a release, update the CHANGELOG.md file:

```markdown
## [1.3.0] - 2025-01-24

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix A
- Bug fix B

### Changed
- Updated behavior of Z
```

Commit and push the changes:

```bash
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for v1.3.0"
git push origin main
```

### Step 2: Create and Push a Version Tag

The release process is triggered by pushing a version tag in the format `vX.Y.Z`:

```bash
# Create a new version tag
git tag v1.3.0

# Push the tag to GitHub
git push origin v1.3.0
```

**Important**:
- Tag format must be `vX.Y.Z` (e.g., `v1.0.0`, `v1.2.3`, `v2.0.0`)
- The `v` prefix is required
- Version must follow semantic versioning (MAJOR.MINOR.PATCH)

### Step 3: Automated Workflow Executes

Once the tag is pushed, the GitHub Actions workflow automatically:

1. **Build** (2-3 minutes)
   - Checks out the repository with full git history
   - Sets up Python 3.11
   - Installs build dependencies
   - Extracts version from the git tag
   - Builds source distribution (.tar.gz) and wheel (.whl)
   - Uploads build artifacts

2. **Publish to PyPI** (1-2 minutes)
   - Downloads build artifacts
   - Uses trusted publishing (OIDC) to authenticate with PyPI
   - Publishes the package to https://pypi.org/p/introligo

3. **Create GitHub Release** (1 minute)
   - Downloads build artifacts
   - Extracts release notes from CHANGELOG.md for the version
   - Creates a GitHub release with the tag
   - Attaches distribution files (.tar.gz and .whl)

4. **Test Installation** (3-5 minutes)
   - Waits 60 seconds for PyPI to propagate
   - Tests installation on Python 3.8, 3.9, 3.10, 3.11, and 3.12
   - Verifies the package can be imported
   - Checks the CLI works (`introligo --help`)

**Total time**: ~7-12 minutes from tag push to PyPI availability

### Step 4: Verify the Release

1. **Check GitHub Actions**: Visit the [Actions tab](https://github.com/JakubBrzezo/introligo/actions) and verify all jobs passed

2. **Check PyPI**: Visit https://pypi.org/project/introligo/ to see the new version

3. **Check GitHub Releases**: Visit https://github.com/JakubBrzezo/introligo/releases to see the new release

4. **Test locally**:
   ```bash
   pip install --upgrade introligo
   python -c "import introligo; print(introligo.__version__)"
   ```

## Version Numbering

Introligo uses **setuptools_scm** for automatic version management:

- Version is extracted from git tags automatically
- Format: `vMAJOR.MINOR.PATCH` (e.g., `v1.3.0`)
- During development (between releases), version is `X.Y.Z.devN+gHASH`
- On release, version is clean `X.Y.Z`

### Semantic Versioning Guidelines

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.Y.0): Add functionality in a backwards-compatible manner
- **PATCH** version (0.0.Z): Backwards-compatible bug fixes

Examples:
- `v1.0.0` → `v1.0.1`: Bug fix
- `v1.0.1` → `v1.1.0`: New feature (backwards-compatible)
- `v1.1.0` → `v2.0.0`: Breaking change

## Troubleshooting

### Error: "invalid-pending-publisher: valid token, but project already exists"

This error occurs when trying to use trusted publishing on an **existing** PyPI project that hasn't been configured for it yet.

**Solution**:
1. Go to https://pypi.org/manage/project/introligo/settings/publishing/
2. Add the trusted publisher configuration (see Prerequisites section above)
3. The configuration must be added to the **existing project**, not as a "pending publisher"

### Release failed during build

Check the build logs in GitHub Actions. Common issues:
- Invalid tag format (must be `vX.Y.Z`)
- Build dependencies missing (check pyproject.toml)

**Fix**: Delete the tag, fix the issue, and create a new tag:
```bash
git tag -d v1.3.0
git push origin :refs/tags/v1.3.0
# Fix the issue, then create a new tag
git tag v1.3.1
git push origin v1.3.1
```

### Publish to PyPI failed

Check the publish job logs. Common issues:
- Trusted publishing not configured correctly on PyPI
- Version already exists on PyPI
- Package name conflict

**Fix**:
- Verify trusted publishing settings on PyPI (see error above)
- If version exists, increment the version and create a new tag (e.g., `v1.3.1`)

### Test installation failed

This can happen if:
- PyPI takes longer than 60 seconds to propagate
- Network issues

**Fix**: Usually self-resolves. The package is still published successfully. You can re-run the failed job in GitHub Actions.

### Version not detected correctly

If `setuptools_scm` can't detect the version:
- Ensure the repository has git tags: `git tag -l`
- Ensure full git history is available (not a shallow clone)
- Check `pyproject.toml` has correct `[tool.setuptools_scm]` configuration

## Manual Release (Not Recommended)

If you need to publish manually:

```bash
# Install build tools
pip install build twine setuptools-scm[toml]

# Build the package
python -m build

# Upload to PyPI (requires API token)
python -m twine upload dist/*
```

## Development Version

When working on the main branch without a tag, the version will be:
```
X.Y.Z.devN+gHASH
```

For example: `1.3.0.dev5+g1a2b3c4`

This ensures development versions are always unique and sorted correctly.

## Workflow Files

- `.github/workflows/publish-pypi.yml`: Main PyPI publishing workflow
- `.github/workflows/tests.yml`: Run tests on push/PR
- `.github/workflows/deploy-docs.yml`: Deploy documentation to GitHub Pages

## Configuration Files

- `pyproject.toml`: Package metadata, dependencies, and setuptools_scm config
- `introligo/_version.py`: Auto-generated by setuptools_scm (in .gitignore)
- `introligo/__init__.py`: Imports version from `_version.py`

## Best Practices

1. **Always update CHANGELOG.md** before releasing
2. **Test thoroughly** on the main branch before tagging
3. **Use semantic versioning** consistently
4. **Don't delete tags** unless absolutely necessary
5. **Monitor the GitHub Actions** workflow after pushing a tag
6. **Verify installation** after release is complete
7. **Configure trusted publishing** before your first automated release

## Questions?

For issues with the release process:
- Check existing [GitHub Actions runs](https://github.com/JakubBrzezo/introligo/actions)
- Review [PyPI trusted publishing docs](https://docs.pypi.org/trusted-publishers/)
- Review [PyPI trusted publishing troubleshooting](https://docs.pypi.org/trusted-publishers/troubleshooting/)
- Open an issue at https://github.com/JakubBrzezo/introligo/issues
