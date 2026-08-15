# 08 — Realtime

## Overview

PocketBase uses Server-Sent Events (SSE) for realtime subscriptions. By default, realtime events fire for record create/update/delete operations and OAuth2 auth redirects. Custom topics are also supported.

Idle timeout: 5 minutes. Absolute max: 30 minutes (`RealtimeConnectRequestEvent.MaxTimeout`). Connections auto-reconnect.

## Client SDK Subscriptions

### JavaScript SDK

```javascript
import PocketBase from 'pocketbase'
const pb = new PocketBase('http://127.0.0.1:8090')

// Subscribe to all changes in a collection
const unsubscribeAll = pb.collection('articles').subscribe('*', (e) => {
    console.log(e.action)   // "create", "update", "delete"
    console.log(e.record)   // the record data
})

// Subscribe to specific record
const unsubscribeOne = pb.collection('articles').subscribe('RECORD_ID', (e) => {
    console.log(e.action, e.record)
})

// Unsubscribe
unsubscribeAll()
unsubscribeOne()

// Custom topic
const unsubscribeCustom = pb.realtime.subscribe('myTopic', (e) => {
    console.log(e.data)
})
unsubscribeCustom()

// Unsubscribe all
await pb.realtime.unsubscribe()
```

### Dart SDK

```dart
import 'package:pocketbase/pocketbase.dart'

final pb = PocketBase('http://127.0.0.1:8090')

// Subscribe to collection
pb.collection('articles').subscribe('*', (e) {
    print(e.action)
    print(e.record)
})

// Custom topic
pb.realtime.subscribe('myTopic', (e) {
    print(e.data)
})

// Unsubscribe
pb.realtime.unsubscribe('myTopic')
pb.realtime.unsubscribe()  // all
```

## Custom Topics (Go)

```go
func notify(app core.App, subscription string, data any) error {
    rawData, err := json.Marshal(data)
    if err != nil {
        return err
    }

    message := subscriptions.Message{
        Name: subscription,
        Data: rawData,
    }

    group := new(errgroup.Group)

    chunks := app.SubscriptionsBroker().ChunkedClients(300)

    for _, chunk := range chunks {
        group.Go(func() error {
            for _, client := range chunk {
                if !client.HasSubscription(subscription) {
                    continue
                }
                client.Send(message)
            }
            return nil
        })
    }

    return group.Wait()
}

// Usage
err := notify(app, "example", map[string]any{"test": 123})
```

## Client Access Control

Realtime subscriptions respect collection API rules. The `listRule` controls who can subscribe. Authenticated users send their auth token with the subscription request.

```javascript
// Authenticate first
await pb.collection('users').authWithPassword('user@example.com', 'pass')

// Now subscribe (uses auth token)
pb.collection('articles').subscribe('*', (e) => {
    console.log(e.record)
})
```

## Realtime Hooks

```go
// Before connection
app.OnRealtimeConnectRequest().BindFunc(func(e *core.RealtimeConnectRequestEvent) error {
    // e.Client — the connecting client
    // e.App — the app instance
    // e.MaxTimeout — absolute max duration (default 30min)

    // Check IP, rate limit, etc.
    return e.Next()
})

// Before message (record events only)
app.OnRealtimeMessageRequest().BindFunc(func(e *core.RealtimeMessageRequestEvent) error {
    // e.Message — the message being sent
    // e.Client — the target client

    return e.Next()
})
```

```javascript
// JS hooks
onRealtimeConnectRequest((e) => {
    // e.client, e.app
    e.next()
})

onRealtimeMessageRequest((e) => {
    // e.message, e.client
    e.next()
})
```

## Getting Connected Clients

```go
// All clients
clients := app.SubscriptionsBroker().Clients()

// Chunked (for parallel processing)
chunks := app.SubscriptionsBroker().ChunkedClients(300)

// Get auth record for a client
authRecord := client.Get(apis.RealtimeClientAuthKey)
```

## Realtime Event Structure

```javascript
{
    action: "create" | "update" | "delete",
    record: {
        id: "...",
        collectionId: "...",
        collectionName: "...",
        // ... record fields
    }
}
```

## Notes

- View collections don't receive realtime events (no create/update/delete operations)
- A single user can have multiple active connections (different tabs, devices)
- Hidden fields are hidden from realtime events for non-superusers (unless `Unhide` is called)
- Realtime connections use the same HTTP port as the API
- Behind reverse proxy, set `proxy_read_timeout 360s` (NGINX) for long-lived connections
