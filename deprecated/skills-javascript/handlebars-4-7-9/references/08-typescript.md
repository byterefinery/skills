# TypeScript Types

Handlebars 4.7.9 bundles TypeScript definitions in `types/index.d.ts`.

## Core types

```ts
! Template function signature
type TemplateDelegate<T = any> = (context: T, options?: RuntimeOptions) => string;

! Template can be a function or a string (for lazy compilation)
type Template<T = any> = TemplateDelegate<T> | string;

! Backward compatibility alias
type HandlebarsTemplateDelegate<T = any> = TemplateDelegate<T>;

! Template registry
interface HandlebarsTemplates {
  [index: string]: HandlebarsTemplateDelegate;
}

! Runtime options
type RuntimeOptions = Handlebars.RuntimeOptions;
```

## RuntimeOptions

```ts
interface RuntimeOptions {
  partial?: boolean;
  depths?: any[];
  helpers?: { [name: string]: Function };
  partials?: { [name: string]: Template };
  decorators?: { [name: string]: Function };
  data?: any;
  blockParams?: any[];
  allowCallsToHelperMissing?: boolean;
  allowedProtoProperties?: { [name: string]: boolean };
  allowedProtoMethods?: { [name: string]: boolean };
  allowProtoPropertiesByDefault?: boolean;
  allowProtoMethodsByDefault?: boolean;
}
```

## Helper types

```ts
interface HelperOptions {
  fn: TemplateDelegate;
  inverse: TemplateDelegate;
  hash: Record<string, any>;
  data?: any;
}

! Helper function signature (up to 5 positional args + options)
interface HelperDelegate {
  (context?: any, arg1?: any, arg2?: any, arg3?: any, arg4?: any, arg5?: any, options?: HelperOptions): any;
}

! Multiple helper registration
interface HelperDeclareSpec {
  [key: string]: HelperDelegate;
}
```

## CompileOptions

```ts
interface CompileOptions {
  data?: boolean;
  compat?: boolean;
  knownHelpers?: KnownHelpers;
  knownHelpersOnly?: boolean;
  noEscape?: boolean;
  strict?: boolean;
  assumeObjects?: boolean;
  preventIndent?: boolean;
  ignoreStandalone?: boolean;
  explicitPartialContext?: boolean;
}

type KnownHelpers = {
  [name in BuiltinHelperName | CustomHelperName]: boolean;
};

type BuiltinHelperName =
  | 'helperMissing'
  | 'blockHelperMissing'
  | 'each'
  | 'if'
  | 'unless'
  | 'with'
  | 'log'
  | 'lookup';

type CustomHelperName = string;

interface PrecompileOptions extends CompileOptions {
  srcName?: string;
  destName?: string;
}
```

## ParseOptions

```ts
interface ParseOptions {
  srcName?: string;
  ignoreStandalone?: boolean;
}
```

## Public API

```ts
namespace Handlebars {
  ! Registration
  function registerHelper(name: string, fn: HelperDelegate): void;
  function registerHelper(name: HelperDeclareSpec): void;
  function unregisterHelper(name: string): void;

  function registerPartial(name: string, fn: Template): void;
  function registerPartial(spec: { [name: string]: Template }): void;
  function unregisterPartial(name: string): void;

  function registerDecorator(name: string, fn: Function): void;
  function unregisterDecorator(name: string): void;

  ! Compilation
  function compile<T = any>(input: any, options?: CompileOptions): TemplateDelegate<T>;
  function precompile(input: any, options?: PrecompileOptions): TemplateSpecification;
  function template<T = any>(precompilation: TemplateSpecification): TemplateDelegate<T>;

  ! Parsing
  function parse(input: string, options?: ParseOptions): hbs.AST.Program;
  function parseWithoutProcessing(input: string, options?: ParseOptions): hbs.AST.Program;

  ! Utilities
  function create(): typeof Handlebars;
  function createFrame(object: any): any;
  function blockParams(obj: any[], ids: any[]): any[];
  function log(level: number, obj: any): void;
  function noConflict(): typeof Handlebars;

  ! Properties
  const escapeExpression: typeof Utils.escapeExpression;
  const logger: Logger;
  const templates: HandlebarsTemplates;
  const helpers: { [name: string]: HelperDelegate };
  const partials: { [name: string]: any };
  const decorators: { [name: string]: Function };
  const VERSION: string;

  ! Classes
  class Exception {
    constructor(message: string, node?: hbs.AST.Node);
    description: string;
    fileName: string;
    lineNumber?: any;
    endLineNumber?: any;
    message: string;
    name: string;
    number: number;
    stack?: string;
    column?: any;
    endColumn?: any;
  }

  class SafeString {
    constructor(str: string);
    toString(): string;
    toHTML(): string;
  }

  class Visitor {
    accept(node: hbs.AST.Node): void;
    acceptKey(node: hbs.AST.Node, name: string): void;
    acceptArray(arr: hbs.AST.Expression[]): void;
    ! ... one method per AST node type
  }
}
```

## Utils namespace

```ts
namespace Handlebars.Utils {
  function escapeExpression(str: any): string;
  function createFrame(object: any): any;
  function blockParams(obj: any[], ids: any[]): any[];
  function isEmpty(obj: any): boolean;
  function extend(obj: any, ...source: any[]): any;
  function toString(obj: any): string;
  function isArray(obj: any): boolean;
  function isFunction(obj: any): boolean;
}
```

## AST types

```ts
namespace hbs.AST {
  interface Node {
    type: string;
    loc: SourceLocation;
  }

  interface SourceLocation {
    source: string;
    start: Position;
    end: Position;
  }

  interface Position {
    line: number;
    column: number;
  }

  interface Program extends Node {
    body: Statement[];
    blockParams: string[];
  }

  interface Statement extends Node {}

  interface MustacheStatement extends Statement {
    type: 'MustacheStatement';
    path: PathExpression | Literal;
    params: Expression[];
    hash: Hash;
    escaped: boolean;
    strip: StripFlags;
  }

  interface BlockStatement extends Statement {
    type: 'BlockStatement';
    path: PathExpression;
    params: Expression[];
    hash: Hash;
    program: Program;
    inverse: Program;
    openStrip: StripFlags;
    inverseStrip: StripFlags;
    closeStrip: StripFlags;
  }

  interface PartialStatement extends Statement {
    type: 'PartialStatement';
    name: PathExpression | SubExpression;
    params: Expression[];
    hash: Hash;
    indent: string;
    strip: StripFlags;
  }

  interface PartialBlockStatement extends Statement {
    type: 'PartialBlockStatement';
    name: PathExpression | SubExpression;
    params: Expression[];
    hash: Hash;
    program: Program;
    openStrip: StripFlags;
    closeStrip: StripFlags;
  }

  interface ContentStatement extends Statement {
    type: 'ContentStatement';
    value: string;
    original: StripFlags;
  }

  interface CommentStatement extends Statement {
    type: 'CommentStatement';
    value: string;
    strip: StripFlags;
  }

  interface Expression extends Node {}

  interface SubExpression extends Expression {
    type: 'SubExpression';
    path: PathExpression;
    params: Expression[];
    hash: Hash;
  }

  interface PathExpression extends Expression {
    type: 'PathExpression';
    data: boolean;
    depth: number;
    parts: string[];
    original: string;
  }

  interface Literal extends Expression {}

  interface StringLiteral extends Literal {
    type: 'StringLiteral';
    value: string;
    original: string;
  }

  interface BooleanLiteral extends Literal {
    type: 'BooleanLiteral';
    value: boolean;
    original: boolean;
  }

  interface NumberLiteral extends Literal {
    type: 'NumberLiteral';
    value: number;
    original: number;
  }

  interface UndefinedLiteral extends Literal {
    type: 'UndefinedLiteral';
  }

  interface NullLiteral extends Literal {
    type: 'NullLiteral';
  }

  interface Hash extends Node {
    type: 'Hash';
    pairs: HashPair[];
  }

  interface HashPair extends Node {
    type: 'HashPair';
    key: string;
    value: Expression;
  }

  interface StripFlags {
    open: boolean;
    close: boolean;
  }

  interface helpers {
    helperExpression(node: Node): boolean;
    scopeId(path: PathExpression): boolean;
    simpleId(path: PathExpression): boolean;
  }
}
```

## Logger type

```ts
interface Logger {
  DEBUG: number;
  INFO: number;
  WARN: number;
  ERROR: number;
  level: number;
  methodMap: { [level: number]: string };
  log(level: number, obj: string): void;
}
```

## Module declarations

```ts
declare module "handlebars" {
  export = Handlebars;
}

declare module "handlebars/runtime" {
  export = Handlebars;
}
```

## Typing notes

- `HelperDelegate` supports up to 5 positional arguments before `options`. For helpers with more args, use rest parameters or type the helper directly.
- `TemplateSpecification` is an empty interface — the actual spec shape is internal and not exposed in types.
- `Handlebars.compile()` accepts `any` for input to support both strings and pre-parsed ASTs.
- The `hbs` namespace contains internal types (AST nodes, Utils, SafeString) that are re-exported from the main `Handlebars` namespace where applicable.
