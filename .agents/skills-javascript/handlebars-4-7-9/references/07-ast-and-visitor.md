# AST and Visitor

## Parse API

```js
! Parse template string into AST
const ast = Handlebars.parse(source, options);

! Parse without whitespace processing
const ast = Handlebars.parseWithoutProcessing(source, options);
```

`Handlebars.parse()` runs the raw parser output through the `WhitespaceControl` visitor which processes `~` markers and standalone detection. `parseWithoutProcessing()` skips this step.

Both methods validate pre-parsed ASTs if a `Program` node is passed directly, checking:
- `PathExpression.depth` is a non-negative integer
- `PathExpression.parts` is a string array
- `NumberLiteral.value` is a finite number
- `BooleanLiteral.value` is a boolean

## AST node types

### Program

Root node. Contains the template body and block params.

```js
{
  type: 'Program',
  body: [Statement],
  blockParams: [string],
  loc: SourceLocation
}
```

### Statements

All statement types extend `Node` (have `type` and `loc`):

#### MustacheStatement

Simple `{{ }}` expressions.

```js
{
  type: 'MustacheStatement',
  path: PathExpression | Literal,
  params: [Expression],
  hash: Hash,
  escaped: boolean,
  strip: { open: boolean, close: boolean }
}
```

#### BlockStatement

Block expressions: `{{#if}}`, `{{#each}}`, custom block helpers.

```js
{
  type: 'BlockStatement',
  path: PathExpression,
  params: [Expression],
  hash: Hash,
  program: Program,
  inverse: Program | null,
  openStrip: { open: boolean, close: boolean },
  inverseStrip: { open: boolean, close: boolean },
  closeStrip: { open: boolean, close: boolean }
}
```

#### PartialStatement

Partial invocation: `{{> name}}`.

```js
{
  type: 'PartialStatement',
  name: PathExpression | SubExpression,
  params: [Expression],
  hash: Hash,
  indent: string,
  strip: { open: boolean, close: boolean }
}
```

#### PartialBlockStatement

Partial block: `{{#> name}}...{{/name}}`.

```js
{
  type: 'PartialBlockStatement',
  name: PathExpression | SubExpression,
  params: [Expression],
  hash: Hash,
  program: Program,
  openStrip: { open: boolean, close: boolean },
  closeStrip: { open: boolean, close: boolean }
}
```

#### Decorator

Standalone decorator: `{{*logRender}}`.

Same structure as `MustacheStatement`.

#### DecoratorBlock

Block decorator: `{{#*inline "name"}}...{{/inline}}`.

Same structure as `BlockStatement`.

#### ContentStatement

Plain text content between expressions.

```js
{
  type: 'ContentStatement',
  value: string,
  original: string
}
```

#### CommentStatement

Template comments: `{{! comment}}` or `{{!-- comment --}}`.

```js
{
  type: 'CommentStatement',
  value: string,
  strip: { open: boolean, close: boolean }
}
```

### Expressions

All expressions extend `Node`:

#### SubExpression

Nested expressions: `(upper name)`.

```js
{
  type: 'SubExpression',
  path: PathExpression,
  params: [Expression],
  hash: Hash
}
```

#### PathExpression

Property paths: `name`, `user.name`, `../name`, `@root`.

```js
{
  type: 'PathExpression',
  data: boolean,      ! true for @-prefixed paths
  depth: number,      ! number of .. segments
  parts: [string],    ! path segments
  original: string    ! original source text
}
```

#### Literals

```js
! StringLiteral
{ type: 'StringLiteral', value: string, original: string }

! NumberLiteral
{ type: 'NumberLiteral', value: number, original: number }

! BooleanLiteral
{ type: 'BooleanLiteral', value: boolean, original: boolean }

! UndefinedLiteral
{ type: 'UndefinedLiteral' }

! NullLiteral
{ type: 'NullLiteral' }
```

#### Hash

Named arguments: `key=value`.

```js
{
  type: 'Hash',
  pairs: [HashPair]
}

! HashPair
{
  type: 'HashPair',
  key: string,
  value: Expression
}
```

#### SourceLocation

```js
{
  source: string,
  start: { line: number, column: number },
  end: { line: number, column: number }
}
```

## Visitor pattern

`Handlebars.Visitor` is the base class for AST traversal. Override node type methods to transform or inspect the AST.

```js
const visitor = new Handlebars.Visitor();
visitor.mutating = false;  ! set true to modify the AST

visitor.accept(ast);
```

### Visitor API

- `accept(node)` — visit a node, dispatching to the appropriate type method
- `acceptKey(node, name)` — visit a child property, updating in-place if `mutating`
- `acceptRequired(node, name)` — like `acceptKey` but throws if result is null
- `acceptArray(array)` — visit array elements, removing null results if `mutating`

### Overridable methods

Each node type has a corresponding method. Return the (possibly modified) node:

```js
const visitor = new Handlebars.Visitor();

visitor.Program = function(program) {
  this.acceptArray(program.body);
  return program;
};

visitor.MustacheStatement = function(mustache) {
  this.acceptRequired(mustache, 'path');
  this.acceptArray(mustache.params);
  this.acceptKey(mustache, 'hash');
  return mustache;
};

visitor.BlockStatement = function(block) {
  this.acceptRequired(block, 'path');
  this.acceptArray(block.params);
  this.acceptKey(block, 'hash');
  this.acceptKey(block, 'program');
  this.acceptKey(block, 'inverse');
  return block;
};

! Leaf nodes (no children to visit):
visitor.ContentStatement = function() {};
visitor.CommentStatement = function() {};
visitor.PathExpression = function() {};
visitor.StringLiteral = function() {};
visitor.NumberLiteral = function() {};
visitor.BooleanLiteral = function() {};
visitor.UndefinedLiteral = function() {};
visitor.NullLiteral = function() {};

visitor.Hash = function(hash) {
  this.acceptArray(hash.pairs);
  return hash;
};

visitor.HashPair = function(pair) {
  this.acceptRequired(pair, 'value');
  return pair;
};
```

### WhitespaceControl

`WhitespaceControl` is a Visitor subclass that processes `~` markers and standalone detection. It modifies `ContentStatement` values to strip whitespace.

```js
const WhitespaceControl = require('handlebars/compiler/whitespace-control');
const strip = new WhitespaceControl(options);
const processed = strip.accept(ast);
```

Key behaviors:
- `~` after `{{` strips preceding whitespace/newline
- `~` before `}}` strips following whitespace/newline
- Standalone mustaches (alone on a line) strip surrounding newlines
- For partials on standalone lines, the indent is captured for auto-indentation

## AST helpers

`Handlebars.AST.helpers` provides utility functions for classifying nodes:

```js
! Check if a node is definitely a helper expression
Handlebars.AST.helpers.helperExpression(node);
! Returns true for SubExpressions, or Mustache/Block with params or hash

! Check if a path is scoped (starts with . or this)
Handlebars.AST.helpers.scopedId(path);

! Check if a path is simple (single part, not scoped, no depth)
Handlebars.AST.helpers.simpleId(path);
```

## Compiler

`Handlebars.Compiler` transforms the AST into an intermediate representation (opcodes):

```js
const compiler = new Handlebars.Compiler();
const environment = compiler.compile(ast, options);
! environment.opcodes — array of { opcode, args, loc }
! environment.children — array of child compilers
! environment.usePartial, useDepths, useBlockParams, etc.
```

## JavaScriptCompiler

`Handlebars.JavaScriptCompiler` transforms the opcode IR into JavaScript source:

```js
const jsCompiler = new Handlebars.JavaScriptCompiler();
const source = jsCompiler.compile(environment, options);
! source is a string of JavaScript
```

Or get a template spec object (used by `Handlebars.template()`):

```js
const spec = jsCompiler.compile(environment, options, undefined, true);
const tpl = Handlebars.template(spec);
```

## Printer

`Handlebars.Compiler.printer` can pretty-print AST nodes back to template source (useful for debugging and transformation tools).
