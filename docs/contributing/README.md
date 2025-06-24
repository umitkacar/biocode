# 🤝 Contributing to BioCode

Thank you for your interest in contributing to BioCode! This guide will help you get started.

## 📋 Ways to Contribute

### 🐛 Report Bugs
- Use the [issue tracker](https://github.com/umitkacar/biocode/issues)
- Include reproduction steps
- Provide system information
- Attach relevant logs

### 💡 Suggest Features
- Open a [discussion](https://github.com/umitkacar/biocode/discussions)
- Explain the biological metaphor
- Describe use cases
- Consider implementation

### 📝 Improve Documentation
- Fix typos and errors
- Add examples
- Clarify explanations
- Translate content

### 💻 Submit Code
- Fix bugs
- Implement features
- Improve performance
- Add tests

## 🚀 Getting Started

1. **[Development Setup](development-setup.md)** - Set up your environment
2. **[Testing Guide](testing.md)** - Write and run tests
3. **[Code Standards](../development/code-style.md)** - Follow our style

## 📖 Contribution Process

### 1. Fork and Clone
```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/biocode.git
cd biocode
git remote add upstream https://github.com/umitkacar/biocode.git
```

### 2. Create Branch
```bash
# For features
git checkout -b feature/cell-memory

# For fixes
git checkout -b fix/tissue-inflammation

# For docs
git checkout -b docs/update-tutorial
```

### 3. Make Changes
- Follow [code style](../development/code-style.md)
- Add/update tests
- Update documentation
- Use biological metaphors

### 4. Test
```bash
# Run tests
pytest

# Check style
pre-commit run --all-files

# Test examples
python examples/basic_usage.py
```

### 5. Commit
```bash
# Use conventional commits
git commit -m "feat: add long-term memory to cells"
git commit -m "fix: prevent tissue inflammation cascade"
git commit -m "docs: clarify organ transplant process"
```

### 6. Push and PR
```bash
git push origin your-branch
```
Then create a Pull Request on GitHub.

## 🎯 Pull Request Guidelines

### PR Title
Use conventional commit format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style
- `refactor:` Refactoring
- `test:` Tests
- `chore:` Maintenance

### PR Description
Include:
- What changes were made
- Why they were needed
- How they were tested
- Related issues

### PR Checklist
- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] Biological metaphors consistent
- [ ] No breaking changes (or documented)

## 🧬 Biological Consistency

When contributing, maintain biological accuracy:

### Good Examples
✅ "Cell enters hibernation state during low resources"
✅ "Tissue inflammation triggers immune response"
✅ "Organ compatibility check before transplant"

### Poor Examples
❌ "Cell reboots after crash"
❌ "Tissue performs garbage collection"
❌ "Organ defragmentation process"

## 🏗️ Architecture Guidelines

### Adding New Cell Types
1. Extend `EnhancedCodeCell`
2. Define specialized organelles
3. Implement unique behaviors
4. Add to tissue registry

### Creating New Organs
1. Compose multiple tissues
2. Define organ-specific functions
3. Implement health monitoring
4. Add compatibility rules

## 🔍 Code Review Process

All PRs go through review:
1. Automated checks (tests, style)
2. Biological accuracy review
3. Code quality review
4. Documentation review

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what's best for the project
- Use welcoming language

## 🎖️ Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](../../CONTRIBUTORS.md)
- Release notes
- Documentation credits

## 💬 Getting Help

- Check [existing issues](https://github.com/umitkacar/biocode/issues)
- Ask in [discussions](https://github.com/umitkacar/biocode/discussions)
- Join our community chat
- Email: biocode@example.com

## 🙏 Thank You!

Every contribution, no matter how small, helps make BioCode better. We appreciate your time and effort!

---

Ready to contribute? Start with [Development Setup](development-setup.md)! 🚀