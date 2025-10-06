Common issues and solutions when using markdown includes.

## ❌ Issue: File Not Found Error

### 🔴 Error Message
```
IntroligoError: Markdown file not found: /path/to/file.md
```

### ✅ Solution
Check that the path is relative to the configuration file:

```yaml
# If config is at: docs/composition/introligo_config.yaml
# And markdown is at: docs/composition/markdown/guide.md

# ✅ Correct
markdown_includes: "markdown/guide.md"

# ❌ Wrong - absolute path
markdown_includes: "/docs/composition/markdown/guide.md"

# ❌ Wrong - relative to project root
markdown_includes: "docs/composition/markdown/guide.md"
```

### 💡 Quick Fix
Use `ls` from the directory containing your config file to verify the path:
```bash
cd docs/composition
ls markdown/guide.md  # Should show the file
```

---

## ❌ Issue: RST Syntax Errors in Output

### 🔴 Error Message
```
WARNING: Unexpected indentation
ERROR: Unexpected indentation
```

### ✅ Solution
This usually happens with complex markdown. The built-in converter handles:
- Headers (H1-H4)
- Code blocks with triple backticks
- Regular paragraphs
- Lists

For complex markdown, consider:
1. Simplifying the markdown structure
2. Using RST-compatible markdown syntax
3. Breaking into smaller files

---

## ❌ Issue: Code Blocks Not Rendering

### 🔴 Problem
Code blocks appear as plain text instead of highlighted code.

### ✅ Solution
Ensure you're using triple backticks with language specification:

```markdown
# ✅ Correct
```python
def hello():
    print("Hello!")
```

# ❌ Wrong - no language
```
def hello():
    print("Hello!")
```

# ❌ Wrong - indented code (not supported)
    def hello():
        print("Hello!")
```

---

## ❌ Issue: Headers Not Converting

### 🔴 Problem
Headers appear as regular text with `#` symbols.

### ✅ Solution
Make sure there's a space after the `#`:

```markdown
# ✅ Correct
## ✅ Also correct
### ✅ Works great

#❌ Wrong - no space
##❌ Wrong - no space
```

---

## ❌ Issue: Emojis Not Displaying

### 🔴 Problem
Emojis appear as squares or question marks.

### ✅ Solution
Emojis are supported! Make sure:
1. Your markdown file is saved with UTF-8 encoding
2. Your terminal/editor supports UTF-8
3. The Sphinx theme supports emojis (most modern themes do)

Example of working emojis: 🎉 🚀 📝 ✨ 🔧 💡

---

## ❌ Issue: Empty Output

### 🔴 Problem
The markdown content doesn't appear in generated documentation.

### ✅ Solution
Check these common issues:

1. **Verify the field name:**
   ```yaml
   # ✅ Correct
   markdown_includes: "file.md"

   # ❌ Wrong field name
   markdown_include: "file.md"  # Missing 's'
   ```

2. **Check file has content:**
   ```bash
   cat docs/composition/markdown/file.md
   # Should show content, not empty
   ```

3. **Verify it's in the right module:**
   ```yaml
   modules:
     my_module:  # Make sure this is the right module
       markdown_includes: "file.md"
   ```

---

## ❌ Issue: Path Resolution with !include

### 🔴 Problem
Using `!include` with markdown includes causes path issues.

### ✅ Solution
Paths in markdown includes are always relative to the **main config file**, not the included file:

```yaml
# Main config: docs/composition/introligo_config.yaml
modules:
  my_module: !include ../../src/my_module_doc.yaml

# In src/my_module_doc.yaml:
title: "My Module"
# ✅ Path relative to main config file
markdown_includes: "docs/markdown/guide.md"

# ❌ Not relative to my_module_doc.yaml location
markdown_includes: "../docs/markdown/guide.md"
```

---

## 🐛 Debugging Tips

### 1️⃣ Enable Verbose Mode
```bash
python introligo.py config.yaml -o docs -v
```
This shows which markdown files are being included.

### 2️⃣ Use Dry Run
```bash
python introligo.py config.yaml -o docs --dry-run
```
Preview what would be generated without creating files.

### 3️⃣ Check Generated RST
Look at the generated `.rst` file to see the converted content:
```bash
cat docs/generated/my_module.rst
```

### 4️⃣ Test with Simple Markdown First
Create a minimal test file:
```markdown
# Test

This is a test.

## Works?

Yes it does! 🎉
```

---

## 📞 Getting Help

If you encounter issues not covered here:

1. **Check the logs** - Run with `-v` for verbose output
2. **Review the config** - Ensure YAML syntax is correct
3. **Test incrementally** - Add one markdown file at a time
4. **Check file permissions** - Ensure files are readable

## ✨ Pro Tips

- 💡 Start simple and add complexity gradually
- 💡 Keep markdown files focused and modular
- 💡 Use consistent formatting in your markdown
- 💡 Test after each change to catch issues early
- 💡 Use version control to track working configurations

Remember: The markdown converter is designed for documentation use cases. Keep your markdown clean and simple for best results! 🚀
