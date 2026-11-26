# Pub/Sub and Monitor

Source: docs/advanced_features.rst (Publish/Subscribe, Sharded pubsub, Monitor), README.md.

## Subscriptions

```python
p = r.pubsub()
p.subscribe('my-first-channel', 'my-second-channel')
p.psubscribe('my-*')
```

Every message read from a PubSub instance is a dict with keys:

- `type` — one of `'subscribe'`, `'unsubscribe'`, `'psubscribe'`, `'punsubscribe'`, `'message'`, `'pmessage'`
- `channel` — channel (un)subscribed to, or source channel of a message
- `pattern` — pattern that matched a published channel; `None` except for `'pmessage'`
- `data` — for [un]subscribe messages the current number of subscriptions; for [p]message messages the published payload

`r.publish('channel', 'data')` returns the number of matching channel+pattern subscriptions.

## Message Handlers

Pass channels/patterns as keyword arguments mapped to callables to register handlers:

```python
def my_handler(message):
    print('MY HANDLER: ', message['data'])

p.subscribe(**{'my-channel': my_handler})
p.get_message()        # subscribe confirmation
r.publish('my-channel', 'awesome data')
p.get_message()        # handler ran; this call returns None
```

Handlers require the instance to keep reading data (`get_message()`, `listen()`, or `run_in_thread()`). Hide noisy subscription confirmations with `r.pubsub(ignore_subscribe_messages=True)`.

## Reading Strategies

1. **`get_message()`** — non-blocking poll (uses `select`); returns the message dict or `None`. Easy to integrate into your own loop:
   ```python
   while True:
       message = p.get_message()
       if message:
           ...
       time.sleep(0.001)
   ```
2. **`listen()`** — blocking generator: `for message in p.listen(): ...`
3. **`run_in_thread(sleep_time=..., exception_handler=...)`** — runs `get_message()` in a background thread; returns a thread object with `.stop()`. All subscribed channels/patterns **must** have message handlers (otherwise calls are rejected). The optional `exception_handler(ex, pubsub, thread)` receives worker-thread exceptions.

## Semantics

- Encoding follows the creating client: with `decode_responses=False` (default) the `channel`/`pattern`/`data` values are `bytes`; with `True` they are decoded with the client charset.
- PubSub remembers its subscriptions and **re-subscribes on reconnect**; messages published while disconnected are lost.
- Call `p.close()` when done (shuts down the connection).
- `PUBLISH` is executed on the client (`r.publish`), not on the PubSub object — the subscribed connection cannot run other commands.
- Supported introspection: `r.pubsub_channels()`, `r.pubsub_numsub('foo', 'bar')` (returns `[(b'foo', 9001), (b'bar', 42)]`), `r.pubsub_numpat()`.

## Sharded Pub/Sub (Cluster)

Cluster feature that shards channels by slot, using `SSUBSCRIBE`/`SPUBLISH`:

```python
from valkey.cluster import ValkeyCluster, ClusterNode

r = ValkeyCluster(startup_nodes=[ClusterNode('localhost', 6379),
                                 ClusterNode('localhost', 6380)])
p = r.pubsub()
p.ssubscribe('foo')
message = p.get_sharded_message()
# or target a specific node:
message = p.get_sharded_message(target_node=second_node)
```

Clients subscribe via the master responsible for the channel's slot (or a replica).

## Monitor

`r.monitor()` streams every command processed by the server; `listen()` blocks until each command arrives:

```python
with r.monitor() as m:
    for command in m.listen():
        print(command)
```

Cluster mode has `rc.monitor(target_node=None)` on the cluster client.
