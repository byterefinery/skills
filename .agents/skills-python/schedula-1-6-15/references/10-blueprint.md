# Blueprint

## Overview

`BlueDispatcher` and `Blueprint` provide declarative, Flask-integrated model definition. They enable structured API routing and dispatcher composition.

## BlueDispatcher

A Dispatcher with built-in Flask Blueprint support:

```python
from schedula import BlueDispatcher

# Create with Blueprint integration
blue = BlueDispatcher(name='api', blueprint=my_blueprint)

# Add functions as usual
blue.add_function('func', my_func, inputs=['a'], outputs=['b'])

# Register with Flask app
app.register_blueprint(blue.blueprint)
```

## Blueprint

Flask Blueprint wrapper for Dispatcher:

```python
from schedula import Blueprint

bp = Blueprint('my_api')
bp.add_dispatcher(dsp, url='/api')

# Register with Flask app
app.register_blueprint(bp)
```

## Declarative Model Definition

Blueprints support declarative model building:

```python
from schedula import Blueprint, BlueDispatcher

# Define model structure
bp = Blueprint('model')

# Add dispatchers with URL routing
bp.add_dispatcher(data_loader, url='/load')
bp.add_dispatcher(processor, url='/process')
bp.add_dispatcher(saver, url='/save')

# Create BlueDispatcher from blueprint
dsp = BlueDispatcher(name='pipeline', blueprint=bp)
```

## Integration with Web API

BlueDispatcher integrates with `.web()` for automatic endpoint generation:

```python
from schedula import BlueDispatcher

blue = BlueDispatcher(name='service')
blue.add_function('compute', func, inputs=['x'], outputs=['y'])

# Deploy with Blueprint routing
server = blue.web(run=False).site(host='127.0.0.1', port=5000).run()
```

## `_init` Helper

Internal function that initializes BlueDispatcher/Blueprint from function objects:

```python
from schedula.utils.blue import _init

# Converts function to dispatcher if needed
result = _init(function_or_dispatcher)
```

Used internally by `add_function` and `add_dispatcher` to handle both plain functions and Blueprint-wrapped callables.
