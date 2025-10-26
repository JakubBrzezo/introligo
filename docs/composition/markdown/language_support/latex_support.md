# LaTeX & Mathematical Formulas

Introligo provides seamless integration for mathematical formulas and equations using LaTeX syntax in your documentation.

## Overview

Mathematical content can be included in your documentation either inline within text or as standalone equations. Introligo converts LaTeX mathematical notation to formats renderable by Sphinx, using MathJax or similar renderers in the browser.

## Features

✅ **Inline Math** - Mathematical expressions within text
✅ **Block Equations** - Standalone displayed equations
✅ **LaTeX Files** - Include external `.tex` files
✅ **Auto-Configuration** - Automatic MathJax extension
✅ **Rich Syntax** - Full LaTeX math support
✅ **Cross-References** - Numbered equations with labels

## Basic Usage

### Inline with Text

Include math expressions in your YAML descriptions:

```yaml
modules:
  mathematics:
    title: "Mathematical Functions"
    description: |
      The quadratic formula is \\(x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}\\)
      where \\(a \\neq 0\\).
```

**Note:** Use double backslashes (`\\`) in YAML for LaTeX commands.

### Block Equations

```yaml
modules:
  calculus:
    title: "Calculus"
    overview: |
      The fundamental theorem of calculus:

      .. math::

         \\int_a^b f(x)dx = F(b) - F(a)

      where \\(F'(x) = f(x)\\).
```

### LaTeX File Inclusion

```yaml
modules:
  equations:
    title: "Important Equations"
    latex_includes:
      - "equations/maxwell.tex"
      - "equations/schrodinger.tex"
```

## Configuration Fields

| Field | Description | Usage |
|-------|-------------|-------|
| Inline math | `\\(...\\)` | In any text field |
| Block math | `.. math::` directive | In RST content |
| `latex_includes` | List of `.tex` files | Include external LaTeX |

## How It Works

### Processing Pipeline

```
YAML with LaTeX
    ↓
Introligo Generator
    ↓
RST with math directives
    ↓
Sphinx Build
    ↓
HTML with MathJax
    ↓
Beautiful Equations!
```

### Automatic Extension

Introligo automatically adds MathJax when LaTeX content is detected:

```yaml
# No manual configuration needed!
# Introligo detects latex_includes and adds:
sphinx:
  extensions:
    - "sphinx.ext.mathjax"  # Auto-added
```

## Complete Examples

### Inline Mathematics

```yaml
modules:
  algebra:
    title: "Algebraic Equations"
    description: "Solving equations and inequalities"

    overview: |
      A quadratic equation has the form \\(ax^2 + bx + c = 0\\)
      where \\(a \\neq 0\\).

      The solutions are given by:
      \\(x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}\\)

    notes: |
      The discriminant \\(\\Delta = b^2 - 4ac\\) determines:
      - If \\(\\Delta > 0\\): two real solutions
      - If \\(\\Delta = 0\\): one repeated solution
      - If \\(\\Delta < 0\\): two complex solutions
```

### Block Equations

```yaml
modules:
  calculus:
    title: "Calculus Fundamentals"

    overview: |
      **Derivative Definition:**

      .. math::

         f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}

      **Integration by Parts:**

      .. math::

         \\int u\\,dv = uv - \\int v\\,du

      **Taylor Series:**

      .. math::

         f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(a)}{n!}(x-a)^n
```

### Numbered Equations

```yaml
modules:
  physics:
    title: "Physics Equations"

    overview: |
      Einstein's mass-energy equivalence:

      .. math::
         :label: einstein

         E = mc^2

      The kinetic energy equation:

      .. math::
         :label: kinetic

         KE = \\frac{1}{2}mv^2

      From equations :eq:`einstein` and :eq:`kinetic` we can derive...
```

### External LaTeX Files

**equations/fourier.tex:**
```latex
% Fourier Transform
F(\\omega) = \\int_{-\\infty}^{\\infty} f(t) e^{-i\\omega t} dt

% Inverse Fourier Transform
f(t) = \\frac{1}{2\\pi} \\int_{-\\infty}^{\\infty} F(\\omega) e^{i\\omega t} d\\omega
```

**introligo_config.yaml:**
```yaml
modules:
  signal_processing:
    title: "Signal Processing"
    latex_includes:
      - "equations/fourier.tex"
```

## LaTeX Syntax Reference

### Greek Letters

```
\\alpha, \\beta, \\gamma, \\delta, \\epsilon
\\Alpha, \\Beta, \\Gamma, \\Delta, \\Epsilon
\\pi, \\Pi, \\sigma, \\Sigma, \\omega, \\Omega
```

**Output:** α, β, γ, δ, ε, Α, Β, Γ, Δ, Ε, π, Π, σ, Σ, ω, Ω

### Fractions and Roots

```latex
\\frac{numerator}{denominator}
\\sqrt{x}
\\sqrt[n]{x}
```

**Examples:**
- \\(\\frac{1}{2}\\), \\(\\frac{a+b}{c+d}\\)
- \\(\\sqrt{2}\\), \\(\\sqrt[3]{27}\\)

### Superscripts and Subscripts

```latex
x^2         % Superscript
x_i         % Subscript
x^{2n+1}    % Multi-character superscript
x_{i,j}     % Multi-character subscript
```

### Sums and Products

```latex
\\sum_{i=1}^{n} x_i
\\prod_{i=1}^{n} x_i
\\int_{a}^{b} f(x)dx
\\lim_{x \\to \\infty} f(x)
```

### Matrices

```latex
.. math::

   \\begin{pmatrix}
   a & b \\\\
   c & d
   \\end{pmatrix}

   \\begin{bmatrix}
   1 & 0 \\\\
   0 & 1
   \\end{bmatrix}
```

### Common Symbols

```latex
\\leq, \\geq              % ≤, ≥
\\neq, \\approx          % ≠, ≈
\\pm, \\mp               % ±, ∓
\\times, \\div           % ×, ÷
\\infty                  % ∞
\\partial                % ∂
\\nabla                  % ∇
\\cdot, \\cdots          % ·, ⋯
\\in, \\notin            % ∈, ∉
\\subset, \\subseteq     % ⊂, ⊆
\\cap, \\cup             % ∩, ∪
\\rightarrow, \\Rightarrow  % →, ⇒
```

## Advanced Features

### Multi-line Equations

```yaml
overview: |
  System of equations:

  .. math::

     \\begin{align}
     x + y &= 5 \\\\
     2x - y &= 1
     \\end{align}
```

### Cases and Piecewise Functions

```yaml
overview: |
  Absolute value function:

  .. math::

     |x| = \\begin{cases}
     x & \\text{if } x \\geq 0 \\\\
     -x & \\text{if } x < 0
     \\end{cases}
```

### Chemical Formulas

```yaml
overview: |
  Water molecule: \\(\\text{H}_2\\text{O}\\)

  Glucose: \\(\\text{C}_6\\text{H}_{12}\\text{O}_6\\)
```

### Theorems and Proofs

```yaml
modules:
  theorems:
    title: "Mathematical Theorems"

    overview: |
      .. math::
         :label: pythagorean

         a^2 + b^2 = c^2

      **Theorem (Pythagorean):** In a right triangle, the square
      of the hypotenuse equals the sum of squares of the other
      two sides (see :eq:`pythagorean`).
```

## Best Practices

### 1. Use Clear Variable Names

```latex
% Good - clear variable names
E = mc^2

% Less clear
x = yz^2
```

### 2. Add Text Descriptions

```yaml
overview: |
  The formula for kinetic energy:

  .. math::

     KE = \\frac{1}{2}mv^2

  where \\(m\\) is mass and \\(v\\) is velocity.
```

### 3. Group Related Equations

```yaml
modules:
  maxwell:
    title: "Maxwell's Equations"
    latex_includes:
      - "equations/maxwell_gauss.tex"
      - "equations/maxwell_faraday.tex"
      - "equations/maxwell_ampere.tex"
      - "equations/maxwell_magnetic.tex"
```

### 4. Use Consistent Notation

```latex
% Consistent throughout docs
f(x), g(x), h(x)  % Functions
x, y, z           % Variables
a, b, c           % Constants
\\alpha, \\beta, \\gamma  % Parameters
```

### 5. Label Important Equations

```yaml
.. math::
   :label: important_equation

   E = mc^2
```

Then reference with `:eq:`important_equation``.

## Project Structure

```
myproject/
├── docs/
│   ├── introligo_config.yaml
│   ├── equations/
│   │   ├── basics.tex
│   │   ├── advanced.tex
│   │   └── theorems.tex
│   └── (generated files)
└── (source code)
```

## Troubleshooting

### Equations Not Rendering

**Problem:** Math appears as LaTeX source code

**Solution:** Check that MathJax extension is loaded:
```yaml
sphinx:
  extensions:
    - "sphinx.ext.mathjax"  # Should be auto-added
```

### Syntax Errors

**Problem:** `WARNING: Could not lex literal_block as "latex"`

**Solution:** Check LaTeX syntax, common issues:
- Missing backslashes
- Unmatched braces `{}`
- Wrong environment names

### Double Backslash Issues

**Problem:** LaTeX commands not working in YAML

**Solution:** Use double backslashes:
```yaml
# Wrong
description: "Formula: \frac{1}{2}"

# Correct
description: "Formula: \\frac{1}{2}"
```

### File Not Found

**Problem:** `LaTeX file not found: equations/myfile.tex`

**Solution:** Check path is relative to config file:
```yaml
# If config is in docs/
latex_includes:
  - "equations/myfile.tex"  # → docs/equations/myfile.tex
```

## Example: Complete Mathematics Module

```yaml
modules:
  mathematics:
    title: "Mathematical Foundations"
    description: "Core mathematical concepts and formulas"

    overview: |
      This module covers fundamental mathematical concepts
      used throughout the project.

      **Key Concepts:**

      - Algebra: \\(ax^2 + bx + c = 0\\)
      - Calculus: \\(\\frac{dy}{dx}\\), \\(\\int f(x)dx\\)
      - Linear Algebra: matrices and vectors

    features:
      - "Comprehensive equation library"
      - "Clear mathematical notation"
      - "Cross-referenced formulas"

  algebra:
    parent: "mathematics"
    title: "Algebra"
    latex_includes:
      - "math/algebra_basics.tex"
      - "math/quadratic.tex"

  calculus:
    parent: "mathematics"
    title: "Calculus"
    latex_includes:
      - "math/derivatives.tex"
      - "math/integrals.tex"

  linear_algebra:
    parent: "mathematics"
    title: "Linear Algebra"
    latex_includes:
      - "math/matrices.tex"
      - "math/vectors.tex"
```

## Comparison with Other Content

| Content Type | Inclusion Method | Auto-Config |
|--------------|------------------|-------------|
| **LaTeX/Math** | `latex_includes`, inline | ✅ MathJax |
| **Python** | `module` field | ✅ autodoc |
| **C/C++** | Doxygen + `doxygen_*` | ✅ Breathe |
| **Go** | `godoc_*` fields | ⚠️ Manual extraction |
| **Markdown** | `markdown_includes` | N/A |
| **RST** | `rst_includes` | N/A |

## See Also

- [MathJax Documentation](https://www.mathjax.org/)
- [LaTeX Mathematics](https://en.wikibooks.org/wiki/LaTeX/Mathematics)
- [Sphinx Math Support](https://www.sphinx-doc.org/en/master/usage/extensions/math.html)
- [LaTeX Symbol Reference](http://tug.ctan.org/info/symbols/comprehensive/symbols-a4.pdf)

## Summary

Introligo's LaTeX support provides:

✅ **Inline and block equations** - Mathematical content anywhere
✅ **External LaTeX files** - Organize complex formulas
✅ **Auto-configuration** - MathJax automatically added
✅ **Full LaTeX syntax** - Complete mathematical notation
✅ **Cross-references** - Numbered and labeled equations

Add beautiful mathematical formulas to your documentation today!
