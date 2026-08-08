# Web API

## Overview

Convert any Dispatcher to a Flask-based REST API service using the `.web()` method. Requires the `web` extra: `pip install 'schedula[web]'`.

## Basic Usage

```python
# Deploy dispatcher as API server
server = dsp.web(run=False).site(host='127.0.0.1', port=5000).run()
url = server.url  # 'http://127.0.0.1:5000'

# Shutdown
server.shutdown()
```

## Endpoints

### Dispatch Endpoint

```
POST /                      # or POST /{dsp_name}
```

Calls `Dispatcher.dispatch()`. Request body:

```json
{
    "args": [{"a": 1, "b": 2}],
    "kwargs": {"outputs": ["c"]}
}
```

Response:

```json
{
    "return": {"c": 3}
}
```

On error:

```json
{
    "error": "Error message"
}
```

### Function Endpoint

```
POST /{dsp_name}/{function_id}
```

Invokes a specific function directly. Request body:

```json
{
    "kwargs": {"x": 10, "y": 20}
}
```

### Query Parameter: `data`

Append `?data=input,return` to include inputs in response and exclude error messages:

```
POST /dispatcher/encrypt?data=input,return
```

Response:

```json
{
    "input": {"key": "...", "message": "..."},
    "return": {"encrypted": "..."}
}
```

## Server Lifecycle

```python
# Non-blocking start
server = dsp.web(run=False).site(host='0.0.0.0', port=8080).run()

# Server runs until garbage collected or explicitly shutdown
server.shutdown()  # Returns True on success
```

When the `server` object is garbage collected, the Flask app shuts down automatically.

## BlueDispatcher

For more control over the web API, use `BlueDispatcher` or `Blueprint`:

```python
from schedula import BlueDispatcher, Blueprint

# Blueprint for custom routing
bp = Blueprint('my_api')
bp.add_dispatcher(dsp, url='/api')

# BlueDispatcher — dispatcher with Flask Blueprint integration
blue = BlueDispatcher(name='api', blueprint=bp)
```

## Example: Encryption API

```python
import schedula as sh

# Build dispatcher
dsp = sh.Dispatcher(name='crypto')

@sh.add_function(dsp, outputs=['key'])
def generate_key():
    return 'generated-key'

@sh.add_function(dsp, outputs=['encrypted'])
def encrypt(key, message):
    return f"enc({key}:{message})"

@sh.add_function(dsp, outputs=['decrypted'])
def decrypt(key, encrypted):
    return encrypted.split(':', 1)[1].rstrip(')')

# Extract safe sub-model (no file I/O)
api = dsp.get_sub_dsp(['generate_key', 'encrypt', 'decrypt',
                        'key', 'encrypted', 'decrypted', sh.START])

# Deploy
server = api.web(run=False).site(host='127.0.0.1', port=5000).run()

# Use
import requests

# Generate key and encrypt
res = requests.post(
    server.url,
    json={'args': [{'message': 'hello'}]}
).json()

# Decrypt using specific endpoint
res = requests.post(
    f'{server.url}/crypto/decrypt?data=input,return',
    json={'kwargs': res['return']}
).json()

server.shutdown()
```
