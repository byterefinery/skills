# Railroad (grammar) diagrams

Keywords (all beta): `railroad-ebnf-beta` (EBNF, W3C and ISO 14977 styles), `railroad-abnf-beta` (ABNF, RFC 5234), `railroad-peg-beta` (PEG), `railroad-beta` (Mermaid's IR primitives).

Sources: `docs/syntax/railroad.md` at mermaid@12.3.0.

## Common structure

- First line: the diagram keyword.
- Optional `title "..."`, `accTitle:`, `accDescr:`.
- One grammar rule per statement; each rule ends with `;`.

## EBNF

Rules: `rule = definition ;` (`::=` also accepted). Terminals quoted `"text"`/`'text'`; non-terminals are identifiers. Sequence is juxtaposition (W3C) or `,`-separated (ISO 14977); choice `|`; optional `A?` (W3C) or `[ A ]` (ISO); repetition `*`, `+`.

```mermaid
railroad-ebnf-beta
title "Digit Definition"

digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```

```mermaid
railroad-ebnf-beta
title "Optional Sign"

sign = "+" | "-" ;
number = sign? digit+ ;
digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```

## ABNF

Rules: `name = definition ;`; repetition `1*( … )`, `*( … )`; optional `[ … ]`; choice `/`; quoted terminals.

```mermaid
railroad-abnf-beta
title "Phone Number"

phone = [ "+" country-code ] subscriber ;
country-code = 1*DIGIT ;
subscriber = 1*( DIGIT / "-" / " " ) ;
```

## PEG

Rules: `Name <- definition ;`; ordered choice `/`; predicates like `!Keyword`.

```mermaid
railroad-peg-beta
title "Identifiers (keywords excluded)"

Identifier <- !Keyword Letter Letter* ;
Keyword <- "if" / "else" / "while" ;
Letter <- "a" / "b" / "c" / "_" ;
```

## IR primitives (`railroad-beta`)

Explicit constructors: `terminal("text")`, `nonterminal("name")`, `sequence(a, b, ...)`, `choice(a, b, ...)`, `optional(a)`, `zeroOrMore(a)`, `oneOrMore(a)`, `special("text")`. Rules: `rule_name = expression ;`.

Expression grammar (docs, condensed to the verified block):

```mermaid
railroad-beta
title Expression Grammar

expression = sequence(
    nonterminal("term"),
    zeroOrMore(sequence(
        choice(terminal("+"), terminal("-")),
        nonterminal("term")
    ))
) ;
term = sequence(
    nonterminal("factor"),
    zeroOrMore(sequence(
        choice(terminal("*"), terminal("/")),
        nonterminal("factor")
    ))
) ;
factor = choice(
    nonterminal("number"),
    sequence(terminal("("), nonterminal("expression"), terminal(")"))
) ;
```

JSON grammar, semantic version, email address, calculator grammar, and predicates examples — see all-examples "Railroad Diagram" sections for the full verified blocks.
