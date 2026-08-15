# 11 — Testing

## Test Utilities

PocketBase exposes test mocks and stubs in `github.com/pocketbase/pocketbase/tests`:

| Utility | Purpose |
|---|---|
| `tests.TestApp` | In-memory app instance for testing |
| `tests.ApiScenario` | HTTP API test scenario runner |
| `tests.MockMultipartData` | Mock multipart form data |

## Setup

### 1. Prepare test data

```bash
./pocketbase serve --dir="./test_pb_data" --automigrate=0
```

Create test collections and records via Dashboard, then stop the server.

### 2. Test structure

```go
// main_test.go
package main

import (
    "net/http"
    "testing"

    "github.com/pocketbase/pocketbase/core"
    "github.com/pocketbase/pocketbase/tests"
)

const testDataDir = "./test_pb_data"

func generateToken(collectionName, email string) (string, error) {
    app, err := tests.NewTestApp(testDataDir)
    if err != nil {
        return "", err
    }
    defer app.Cleanup()

    record, err := app.FindAuthRecordByEmail(collectionName, email)
    if err != nil {
        return "", err
    }

    return record.NewAuthToken()
}

func TestHelloEndpoint(t *testing.T) {
    superuserToken, err := generateToken(core.CollectionNameSuperusers, "test@example.com")
    if err != nil {
        t.Fatal(err)
    }

    setupTestApp := func(t testing.TB) *tests.TestApp {
        testApp, err := tests.NewTestApp(testDataDir)
        if err != nil {
            t.Fatal(err)
        }
        bindAppHooks(testApp)
        return testApp
    }

    scenarios := []tests.ApiScenario{
        {
            Name:           "guest access denied",
            Method:         http.MethodGet,
            URL:            "/my/hello",
            ExpectedStatus: 401,
            TestAppFactory: setupTestApp,
        },
        {
            Name:   "superuser access",
            Method: http.MethodGet,
            URL:    "/my/hello",
            Headers: map[string]string{
                "Authorization": superuserToken,
            },
            ExpectedStatus: 200,
            ExpectedContent: []string{"Hello world!"},
            TestAppFactory: setupTestApp,
        },
    }

    for _, scenario := range scenarios {
        scenario.Test(t)
    }
}
```

## TestApp

```go
// Create test app from data directory
app, err := tests.NewTestApp("./test_pb_data")
if err != nil {
    t.Fatal(err)
}
defer app.Cleanup()

// Use like regular app
record, err := app.FindRecordById("articles", "RECORD_ID")
```

## ApiScenario

```go
scenario := tests.ApiScenario{
    Name:            "test name",
    Method:          http.MethodPost,
    URL:             "/api/collections/articles/records",
    Headers:         map[string]string{"Authorization": token},
    Body:            strings.NewReader(`{"title": "Test"}`),
    ExpectedStatus:  200,
    ExpectedContent: []string{"\"id\":\""},
    TestAppFactory:  setupTestApp,
}
scenario.Test(t)
```

## MockMultipartData

```go
// Create mock multipart form data for file upload tests
multipartData := tests.MockMultipartData{}
multipartData.AddFile("avatar", "test.jpg", "image/jpeg", []byte("fake image"))
multipartData.AddString("title", "Test title")

req, _ := http.NewRequest(http.MethodPost, "/api/collections/articles/records", &multipartData)
req.Header.Set("Content-Type", multipartData.FormDataContentType())
```

## Running Tests

```bash
go test ./...
go test -v -run TestHelloEndpoint
go test -race ./...
```

## Testing Best Practices

- Use a separate `test_pb_data` directory, not the production one
- Generate tokens once and reuse across scenarios
- Use `TestAppFactory` to create fresh app instances per scenario
- Call `app.Cleanup()` or let scenario handle it
- Test both success and error paths
- Use `ExpectedContent` for partial response body matching
- Test different auth states: guest, user, superuser
