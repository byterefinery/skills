# 03 — mhchem

## Overview

The `mhchem` extension adds `\ce{}` for chemical formulas and `\pu{}` for physical units to KaTeX. It is adapted from the MathJax mhchem extension (v3.3.0) and implements a KaTeX-compatible subset of the [mhchem LaTeX package](https://ctan.org/pkg/mhchem).

## Loading

```js
import "katex/contrib/mhchem";
// or via CDN: <script src="katex/dist/contrib/mhchem.min.js"></script>
```

Must be loaded before any `\ce{}` or `\pu{}` rendering calls.

## \ce{} — Chemical Formulas

### Basic Formulas

```latex
\ce{H2O}           % H₂O
\ce{CO2}           % CO₂
\ce{Na+}           % Na⁺
\ce{Cl-}           % Cl⁻
\ce{SO4^{2-}}      % SO₄²⁻
\ce{Fe^{3+}}       % Fe³⁺
```

### Reactions

```latex
\ce{2H2 + O2 -> 2H2O}
\ce{N2 + 3H2 <=> 2NH3}
\ce{CaCO3 ->[\Delta] CaO + CO2}
\ce{A ->[H2SO4][\Delta] B}
```

Arrow types:

| Syntax | Arrow |
|---|---|
| `->` | Right arrow |
| `<-` | Left arrow |
| `<=>` | Equilibrium (double) arrow |
| `->>` | Right arrow (long) |
| `<<-` | Left arrow (long) |
| `<>` | Equilibrium (single-line) |

Conditions above/below arrows use `->[condition]` or `->[above][below]`.

### States of Matter

```latex
\ce{H2O(l)}        % liquid
\ce{H2O(g)}        % gas
\ce{H2O(s)}        % solid
\ce{NaCl(aq)}      % aqueous
```

### Isotopes and Nuclear

```latex
\ce{^{14}C}        % Carbon-14
\ce{^{235}_{92}U}  % Uranium-235
\ce{_{Z}^{A}X}     % Generic isotope notation
```

### Organic Chemistry

```latex
\ce{CH3CH2OH}      % Ethanol
\ce{CH3-COOH}      % Acetic acid
\ce{Ph-CH3}        % Toluene
\ce{R-X}           % Generic alkyl halide
```

## \pu{} — Physical Units

```latex
\pu{25 mL}
\pu{100 kJ/mol}
\pu{298 K}
\pu{1.5e-3 m/s}
\pu{25 °C}
```

Units are rendered with proper spacing and formatting. Compound units use `/` for division.

## Limitations vs Full mhchem

- Reaction arrows use KaTeX's extensible arrows (not custom arrow glyphs)
- `\rlap`/`\llap` replaced with `\mathrlap`/`\mathllap`
- `\raisebox` used instead of `\raise`
- Triple-dash vertical alignment is slightly adjusted
- Not all mhchem edge cases are covered; complex chemical structures may need manual LaTeX

## Examples

```js
import "katex/contrib/mhchem";

katex.renderToString("\\ce{H2O -> H+ + OH-}");
katex.renderToString("\\ce{Fe^{2+} + Ce^{4+} -> Fe^{3+} + Ce^{3+}}");
katex.renderToString("\\pu{9.81 m/s^2}");
katex.renderToString("\\ce{Ag+(aq) + Cl-(aq) -> AgCl(s)}");
```
