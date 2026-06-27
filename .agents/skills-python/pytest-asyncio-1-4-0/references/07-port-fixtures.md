# Port Fixtures Reference

## Overview

pytest-asyncio provides fixtures for finding unused TCP and UDP ports on localhost. These are useful for binding temporary test servers without port conflicts.

## `unused_tcp_port`

Returns a single unused TCP port number (1024–65535) on `127.0.0.1`.

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_server(unused_tcp_port):
    async def handler(reader, writer):
        writer.close()

    server = await asyncio.start_server(
        handler, host="localhost", port=unused_tcp_port
    )

    # Port is guaranteed free — another server cannot bind to it
    with pytest.raises(OSError):
        await asyncio.start_server(
            handler, host="localhost", port=unused_tcp_port
        )

    server.close()
    await server.wait_closed()
```

## `unused_udp_port`

Returns a single unused UDP port number on `127.0.0.1`.

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_udp_endpoint(unused_udp_port):
    class Protocol:
        def connection_made(self, transport):
            pass

    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        Protocol, local_addr=("127.0.0.1", unused_udp_port)
    )
    transport.abort()
```

## `unused_tcp_port_factory`

A session-scoped callable that returns a different unused TCP port on each invocation. Use when multiple ports are needed in a single test.

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_multiple_servers(unused_tcp_port_factory):
    async def handler(reader, writer):
        writer.close()

    # Each call returns a unique port
    port1 = unused_tcp_port_factory()
    port2 = unused_tcp_port_factory()
    port3 = unused_tcp_port_factory()

    server1 = await asyncio.start_server(handler, "localhost", port1)
    server2 = await asyncio.start_server(handler, "localhost", port2)
    server3 = await asyncio.start_server(handler, "localhost", port3)

    # All three servers run on different ports
    assert port1 != port2 != port3

    for server in (server1, server2, server3):
        server.close()
        await server.wait_closed()
```

The factory tracks produced ports in a session-scoped set to avoid duplicates.

## `unused_udp_port_factory`

Same as TCP factory but for UDP ports.

```python
@pytest.mark.asyncio
async def test_multiple_udp(unused_udp_port_factory):
    port1 = unused_udp_port_factory()
    port2 = unused_udp_port_factory()
    assert port1 != port2
```

## Fixture Summary

| Fixture | Scope | Returns | Use When |
|---------|-------|---------|----------|
| `unused_tcp_port` | function | `int` | Single TCP port needed |
| `unused_udp_port` | function | `int` | Single UDP port needed |
| `unused_tcp_port_factory` | session | `Callable[[], int]` | Multiple TCP ports in one test |
| `unused_udp_port_factory` | session | `Callable[[], int]` | Multiple UDP ports in one test |

## Implementation Details

Ports are found by binding a socket to port 0 (OS assigns an available port), reading the assigned port, then closing the socket. The factory variants maintain a `set()` of produced ports and retry if a duplicate is returned.

## Limitations

- Ports are only guaranteed free at the moment of allocation. Another process could grab the port between fixture return and your `bind()` call.
- Ports are localhost-only (`127.0.0.1`). They do not reserve ports on other interfaces.
- The factory's duplicate avoidance is in-memory (session-scoped). If you need port tracking across pytest sessions, implement your own fixture.
