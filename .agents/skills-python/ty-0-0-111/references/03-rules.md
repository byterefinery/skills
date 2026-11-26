# Rules (ty 0.0.111)

Source: https://docs.astral.sh/ty/reference/rules/ (ty repository docs at tag 0.0.111)

163 rules: 110 default to `error`, 33 to `warn`, 20 to `ignore`. Levels are configurable per rule (and via `all`) through the CLI (`--error`, `--warn`, `--ignore`) or `[tool.ty.rules]`. Query any rule's full documentation, examples, and related issues with `ty explain rule <name>` (omit the name for all rules; `--output-format json` for machine-readable output).

| Rule | Default level | What it checks |
|---|---|---|
| `abstract-and-final-method` | error | Checks for methods decorated with both `@abstractmethod` and `@final`. |
| `abstract-class-instantiation` | error | Checks for direct instantiation of protocol classes and classes with unimplemented abstract methods. |
| `abstract-method-call` | error | Checks for calls to abstract `@classmethod`s or `@staticmethod`s with "trivial bodies" when accessed on the class object itself. |
| `abstract-method-in-final-class` | error | Checks for `@final` classes that have unimplemented abstract methods. |
| `ambiguous-protocol-member` | warn | Checks for protocol classes with members that will lead to ambiguous interfaces. |
| `assert-type-unspellable-subtype` | error | Checks for `assert_type()` calls where the actual type is an unspellable subtype of the asserted type. |
| `blanket-ignore-comment` | ignore | Checks for `ty: ignore` comments that don't specify which rules to ignore. |
| `call-to-function-with-unknown-signature` | error | Detects calls to objects where ty knows that the object is callable, but cannot determine what the signature of the callable object is. |
| `conflicting-declarations` | error | Checks whether a variable has been declared as two conflicting types. |
| `conflicting-metaclass` | error | Checks for class definitions where the metaclass of the class being created would not be a subclass of the metaclasses of all the class's bases. |
| `cyclic-class-definition` | error | Checks for class definitions in stub files that inherit (directly or indirectly) from themselves. |
| `cyclic-type-alias-definition` | error | Checks for circular type alias definitions. |
| `deprecated` | warn | Checks for uses of deprecated items |
| `disjoint-cast` | ignore | Detects `cast` calls where the inferred type of the value is disjoint from the destination type. |
| `disjoint-type-is-narrowing` | error | Checks for `TypeIs[T]` return annotations where `T` is disjoint from and [not assignable to] the declared type of the parameter being narrowed. |
| `division-by-zero` | ignore | It detects division by zero. |
| `duplicate-base` | error | Checks for class definitions with duplicate bases. |
| `duplicate-kw-only` | error | Checks for dataclass definitions with more than one field annotated with `KW_ONLY`. |
| `dynamic-function-decorator-return` | ignore | Detects decorator applications that replace a function with `Any` or another [dynamic type]. |
| `escape-character-in-forward-annotation` | error | Checks for forward annotations that contain escape characters. |
| `experimental-syntax` | warn | Checks for experimental syntax that is not part of the Python typing specification. |
| `final-on-non-method` | error | Checks for `@final` decorators applied to non-method functions. |
| `final-without-value` | error | Checks for `Final` symbols that are declared without a value and are never assigned a value in their scope. |
| `implicit-string-concatenation-in-annotation` | error | Checks for [type expressions][type expression] written as two or more adjacent string literals. |
| `import-not-found` | error | Checks for imports where ty cannot resolve the module. |
| `incompatible-attribute-override` | error | Detects attribute overrides that change whether an inherited attribute is a class variable or an instance variable, expose an incompatible value type, or make a writable attribute read-only. |
| `incompatible-method-override` | error | Detects method overrides that violate the [Liskov Substitution Principle][liskov-substitution-principle] ("LSP"). |
| `incompatible-mutable-override` | error | Detects overrides that narrow the type of a writable attribute. |
| `incompatible-property-override` | error | Detects overrides that change the readable type of an inherited property incompatibly, restrict the values accepted by its setter, or remove a required write operation. |
| `inconsistent-mro` | error | Checks for classes with an inconsistent [method resolution order] (MRO). |
| `inconsistent-overload-decorator` | error | Checks for inconsistent use of decorators on overloaded methods. If one definition uses `@staticmethod` or `@classmethod`, every overload and the implementation, if present, must use the same decorator. |
| `inconsistent-overload-implementation` | error | Checks for overload implementations that are incompatible with one or more overloads. |
| `index-out-of-bounds` | error | Checks for attempts to use an out of bounds index to get an item from a container. |
| `ineffective-final` | warn | Checks for calls to `final()` that type checkers cannot interpret. |
| `instance-layout-conflict` | error | Checks for classes definitions which will fail at runtime due to "instance memory layout conflicts". |
| `invalid-argument-type` | error | Detects call arguments whose type is not assignable to the corresponding typed parameter. |
| `invalid-assignment` | error | Checks for assignments where the type of the value is not [assignable to] the type of the assignee. |
| `invalid-attribute-access` | error | Checks for assignments to class variables from instances and assignments to instance-only attributes from their class. Also checks for reads and writes of generic instance attributes through a generic class or a specialized generic alias. |
| `invalid-await` | error | Checks for `await` being used with types that are not [Awaitable][awaitable-abc]. |
| `invalid-base` | error | Checks for class definitions that have bases which are not instances of `type`. |
| `invalid-context-manager` | error | Checks for expressions used in `with` statements that do not implement the context manager protocol. |
| `invalid-dataclass` | error | Checks for invalid applications of the `@dataclass` decorator. |
| `invalid-dataclass-field-order` | error | Checks for dataclass definitions where required fields are defined after fields with default values. |
| `invalid-dataclass-override` | error | Checks for dataclass definitions that have both `frozen=True` and a custom `__setattr__` or `__delattr__` method defined. |
| `invalid-dataclass-post-init` | error | Checks whether a dataclass's `__post_init__` method accepts the arguments passed by the generated `__init__` method. |
| `invalid-declaration` | error | Checks for declarations where the inferred type of an existing symbol is not [assignable to] its post-hoc declared type. |
| `invalid-enum-member-annotation` | warn | Checks for enum members that have explicit type annotations. |
| `invalid-exception-caught` | error | Checks for exception handlers that catch non-exception classes. |
| `invalid-explicit-override` | error | Checks for methods that are decorated with `@override` but do not override any method in a superclass. |
| `invalid-explicit-return` | error | Checks for `return` statements where the value returned is inconsistent with the function's return-type annotation. |
| `invalid-frozen-dataclass-subclass` | error | Checks for dataclasses with invalid frozen inheritance: |
| `invalid-generator-return-type` | error | Checks whether a generator function's return annotation allows the generator object it produces. |
| `invalid-generic-class` | error | Checks for the creation of invalid generic classes |
| `invalid-generic-enum` | error | Checks for enum classes that are also generic. |
| `invalid-ignore-comment` | warn | Checks for `type: ignore` and `ty: ignore` comments that are syntactically incorrect. |
| `invalid-implicit-return` | error | Detects nonempty functions that can reach the end of their body and implicitly return `None`, despite the fact that their return-type annotations do not allow `None` to be returned. |
| `invalid-implicit-return-in-function-with-stub-body` | error | Detects functions with stub-like bodies whose return-type annotations exclude `None`. |
| `invalid-init-type-variable` | error | Checks for type variables from outer scopes in an explicit annotation of the `self` parameter of `__init__`. |
| `invalid-legacy-positional-parameter` | ignore | Checks for parameters that appear to be attempting to use the legacy convention to specify that a parameter is positional-only, but do so incorrectly. |
| `invalid-legacy-type-variable` | error | Checks for the creation of invalid legacy `TypeVar`s |
| `invalid-match-pattern` | error | Checks for invalid match patterns. |
| `invalid-metaclass` | error | Checks for arguments to `metaclass=` that are invalid. |
| `invalid-module-getattr-call` | error | Checks for imports that fail when calling a module-level `__getattr__` function. |
| `invalid-named-tuple` | error | Checks for invalid definitions of `typing.NamedTuple` and `collections.namedtuple` classes. |
| `invalid-named-tuple-override` | warn | Checks for subclass members that override inherited `NamedTuple` fields. |
| `invalid-newtype` | error | Checks for the creation of invalid `NewType`s |
| `invalid-parameter-default` | error | Checks for default values that can't be assigned to the parameter's annotated type. |
| `invalid-paramspec` | error | Checks for the creation of invalid `ParamSpec`s |
| `invalid-protocol` | error | Checks for protocol classes that are invalid at runtime or do not satisfy the typing specification. |
| `invalid-raise` | error |  |
| `invalid-super-argument` | error | Detects `super()` calls where: |
| `invalid-syntax-in-forward-annotation` | error | Checks for string-literal annotations where the string cannot be parsed as a Python expression. |
| `invalid-total-ordering` | error | Checks for classes decorated with `@functools.total_ordering` that don't define any ordering method (`__lt__`, `__le__`, `__gt__`, or `__ge__`). |
| `invalid-type-alias-type` | error | Checks for the creation of invalid `TypeAliasType`s |
| `invalid-type-arguments` | error | Checks for invalid type arguments in explicit type specialization. |
| `invalid-type-checking-constant` | error | Checks for a value other than `False` assigned to the `TYPE_CHECKING` variable, or an annotation not assignable from `bool`. |
| `invalid-type-form` | error | Checks for expressions that are used as [type expressions] but cannot validly be interpreted as such. |
| `invalid-type-guard-definition` | error | Checks for type guard functions without a first non-self-like non-keyword-only non-variadic parameter. |
| `invalid-type-variable-bound` | error | Checks for [type variables][type variable] whose bounds reference type variables. |
| `invalid-type-variable-constraints` | error | Checks that constrained [type variables] have at least two constraints and that none of their constraints reference type variables. |
| `invalid-type-variable-default` | error | Checks for [type variables] whose default type is not compatible with the type variable's bound or constraints. |
| `invalid-typed-dict-field` | error | Detects invalid `TypedDict` field declarations. |
| `invalid-typed-dict-header` | error | Detects errors in `TypedDict` class headers, such as unexpected arguments or invalid base classes. |
| `invalid-typed-dict-key` | error | Checks for invalid keys when accessing or assigning items on a `TypedDict`. |
| `invalid-typed-dict-statement` | error | Detects statements other than annotated declarations in `TypedDict` class bodies. |
| `invalid-yield` | error | Detects `yield` and `yield from` expressions where the "yield" or "send" type is incompatible with the generator function's annotated return type. |
| `isinstance-against-protocol` | error | Reports invalid runtime checks against `Protocol` classes. This includes explicit calls `isinstance()`/`issubclass()` against non-runtime-checkable protocols, `issubclass()` calls against protocols that have non-method members, and implicit `isinstance()` checks against non-runtime-checkable protocols via pattern matching. |
| `isinstance-against-typed-dict` | error | Reports runtime checks against `TypedDict` classes. This includes explicit calls to `isinstance()`/`issubclass()` and implicit checks performed by `match` class patterns. |
| `lost-keyword-for-regular-parameter` | error | Detects method overrides that rename a positional-or-keyword parameter or make it positional-only. |
| `mismatched-enum-name` | ignore | Checks whether the class name passed to a functional enum constructor, such as `Enum`, `IntEnum`, or `Flag`, differs from the assigned variable's name. |
| `mismatched-namedtuple-name` | ignore | Checks whether the `typename` passed to `typing.NamedTuple` or `collections.namedtuple` differs from the assigned variable's name. |
| `mismatched-newtype-name` | warn | Checks whether the name passed to `NewType` differs from the assigned variable, or if ty cannot determine the value of a string passed to the `name` argument. |
| `mismatched-paramspec-name` | warn | Checks whether the name passed to `ParamSpec` differs from the assigned variable, or if ty cannot determine the value of a string passed to the `name` argument. |
| `mismatched-sentinel-name` | ignore | Checks for `builtins.sentinel` and `typing_extensions.Sentinel` definitions whose name argument does not match the variable they are assigned to. In class scope, the name can be unqualified or include the full enclosing class path. |
| `mismatched-type-alias-name` | warn | Checks whether the name passed to `TypeAliasType` differs from the assigned variable, or if ty cannot determine the value of a string passed to the `name` argument. |
| `mismatched-typeddict-name` | warn | Checks whether the name passed to the functional form of `TypedDict` differs from the assigned variable, or if ty cannot determine the value of a string passed to the `typename` argument. |
| `mismatched-typevar-name` | warn | Checks whether the name passed to `TypeVar` differs from the assigned variable, or if ty cannot determine the value of a string passed to the `name` argument. |
| `mismatched-typevartuple-name` | warn | Checks whether the name passed to `TypeVarTuple` differs from the assigned variable, or if ty cannot determine the value of a string passed to the `name` argument. |
| `misplaced-overload-decorator` | error | Checks for `@final` or `@override` decorators applied to the wrong definition of an overloaded method. If the overload set has an implementation function, put the decorator on the implementation. Otherwise, e.g. in a stub file, put the decorator on the first overload. |
| `missing-argument` | error | Checks for missing required arguments in a call. |
| `missing-attribute` | error | Checks for references to attributes that ty cannot find on the object's type. For a union, this rule applies when every member lacks the attribute. If only some members lack it, ty reports [`missing-union-attribute`](#missing-union-attribute). |
| `missing-direct-dependency` | ignore | Checks for imports from installable packages that the current project or PEP 723 script does not declare as direct dependencies. |
| `missing-module-member` | error | Checks for names in a `from ... import ...` statement that ty cannot find in the resolved module. For a package, an importable submodule also satisfies the import. |
| `missing-overload-implementation` | error | Checks for overloaded functions and methods without a required implementation. An implementation can be omitted in any of the following cases: |
| `missing-override-decorator` | ignore | Checks for methods that override a method or attribute in a superclass but are not decorated with `@override`. |
| `missing-slot` | error | Checks for assignments to declared attributes that have no matching `__slots__` entry on the class or its bases, and no instance dictionary to store their values. |
| `missing-type-argument` | ignore | Checks for generic types used without type parameters in type expressions. |
| `missing-typed-dict-key` | error | Detects missing required keys in `TypedDict` constructor calls. |
| `missing-union-attribute` | error | Checks for reads or deletions of attributes that are present on some members of a union and missing from others. |
| `no-matching-overload` | error | Checks for calls to an overloaded function that do not match any of the overloads. |
| `non-callable-init-subclass` | error | Checks for class definitions that will fail due to non-callable `__init_subclass__` methods. |
| `non-literal-typed-dict-key` | error | Reports attempts to subscript `TypedDict` instances with a key of type `str`. |
| `not-callable` | error | Checks for calls to non-callable objects. |
| `not-iterable` | error | Checks for objects that are not iterable but are used in a context that requires them to be. |
| `not-subscriptable` | error | Checks for subscripting objects that do not support subscripting. |
| `override-of-final-method` | error | Checks for methods on subclasses that override superclass methods decorated with `@final`. |
| `override-of-final-variable` | error | Checks for class variables on subclasses that override a superclass variable that has been declared as `Final`. |
| `parameter-already-assigned` | error | Checks for calls which provide more than one argument for a single parameter. |
| `positional-only-parameter-as-kwarg` | error | Checks for keyword arguments in calls that match positional-only parameters of the callable. |
| `possibly-missing-attribute` | ignore | Checks for possibly missing attributes. |
| `possibly-missing-implicit-call` | warn | Checks for implicit calls to possibly missing methods. |
| `possibly-missing-import` | ignore | Checks for imports of symbols that may be missing. |
| `possibly-missing-submodule` | warn | Checks for accesses of submodules that might not've been imported. |
| `possibly-unresolved-reference` | ignore | Checks for references to names that are possibly not defined. |
| `pydantic-discarded-extra-argument` | warn | Checks for extra keyword arguments that Pydantic silently discards when a model uses `extra="ignore"`, either implicitly or explicitly. |
| `raw-string-type-annotation` | error | Checks for raw-strings in type annotation positions. |
| `redundant-cast` | warn | Detects redundant `cast` calls where the value already has the target type. |
| `redundant-condition` | warn | Detects boolean conditions where the condition can be statically inferred to be always true or always false due to the inferred type of the condition. |
| `redundant-condition-strict` | ignore | Detects boolean conditions where the condition can be statically inferred to be always true or always false. |
| `redundant-final-classvar` | warn | Checks for redundant combinations of the `ClassVar` and `Final` type qualifiers. |
| `renamed-rule-in-ignore-comment` | warn | Checks for renamed rules in `ty: ignore` and `type: ignore[ty:...]` comments. |
| `shadowed-type-variable` | error | Checks for type variables in nested generic classes or functions that shadow type variables from an enclosing scope. |
| `single-overload` | warn | Checks for functions and methods with only one `@overload` declaration. |
| `static-assert-error` | error | Makes sure that the argument of `static_assert` is statically known to be true. |
| `subclass-of-dataclass-with-order` | warn | Checks for classes that inherit from a dataclass with `order=True`. |
| `subclass-of-final-class` | error | Checks for classes that subclass final classes. |
| `super-call-in-named-tuple-method` | error | Checks for calls to `super()` inside methods of `NamedTuple` classes. |
| `suspicious-type-is-narrowing` | warn | Checks for `TypeIs[T]` return annotations where `T` can overlap with the declared type of the parameter being narrowed but is not [assignable to] it. |
| `too-many-positional-arguments` | error | Checks for calls that pass more positional arguments than the callable can accept. |
| `truthiness-test-of-callable` | warn | Detects suspicious truthiness tests of `Callable`-typed values and unions of callable types. |
| `truthiness-test-of-iterable` | warn | Detects boolean conditions where variables typed as `Iterable`, `Iterator`, `Generator` or similar are tested for their truthiness. |
| `truthiness-test-of-none-union` | ignore | Detects truthiness checks of unions with `None` whose non-`None` part can also be falsy, like an `if value: ...` check on a value of type `int \| None`. |
| `type-assertion-failure` | error | Checks for `assert_type()` and `assert_never()` calls where the actual type is not the same as the asserted type. |
| `unavailable-implicit-super-arguments` | error | Detects invalid `super()` calls where implicit arguments like the enclosing class or first method argument are unavailable. |
| `unbound-type-variable` | error | Checks for type variables that are used in a scope where they are not bound to any enclosing generic context. |
| `undefined-reveal` | warn | Checks for calls to `reveal_type` without importing it. |
| `unknown-argument` | error | Checks for keyword arguments in calls that don't match any parameter of the callable. |
| `unknown-rule-in-ignore-comment` | warn | Checks for `ty: ignore[code]` or `type: ignore[ty:code]` comments where `code` isn't a known lint rule. |
| `unknown-typed-dict-constructor-key` | error | Reports `TypedDict` constructions where an unknown key is or may be provided. |
| `unresolved-global` | warn | Detects variables declared as `global` in an inner scope that have no explicit bindings or declarations in the global scope. |
| `unresolved-reference` | error | Checks for references to names that are not defined. |
| `unsound-assignment` | ignore | Detects variable assignments that unsoundly assign a type that is not a [subtype] of a variable's declared type. |
| `unsound-return` | ignore | Detects `return` statements that unsoundly return a type that is not a [subtype] of the function's annotated return type. |
| `unsound-yield` | ignore | Detects `yield` and `yield from` expressions that unsoundly yield a type that is not a [subtype] of the generator function's annotated yield type. |
| `unsupported-base` | warn | Checks for class definitions that have bases which are unsupported by ty. |
| `unsupported-bool-conversion` | error | Checks for bool conversions where the object doesn't correctly implement `__bool__`. |
| `unsupported-dynamic-base` | ignore | Checks for dynamic class definitions (using `type()`) that have bases which are unsupported by ty. |
| `unsupported-operator` | error | Checks for binary expressions, comparisons, and unary expressions where the operands don't support the operator. |
| `unused-awaitable` | warn | Checks for awaitable objects (such as coroutines) used as expression statements without being awaited. |
| `unused-ignore-comment` | warn | Checks for `ty: ignore` directives that are no longer applicable. |
| `unused-type-ignore-comment` | warn | Checks for `type: ignore` directives that are no longer applicable. |
| `useless-overload-body` | warn | Checks for various `@overload`-decorated functions that have non-stub bodies. |
| `zero-stepsize-in-slice` | error | Checks for a step size of zero in slices when the operation is known to fail. |
