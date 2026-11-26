# Routing

Source: `docs/web_quickstart.rst`, `docs/web_advanced.rst`.

## TOC

- Three equivalent styles
- Variable paths
- Named routes and URL reversing
- Class-based views
- Wildcard method
- Static files
- Sub-applications

## Three equivalent styles

1. **Imperative** — `app.add_routes([web.get("/", handler), web.post("/post", post_handler)])`
2. **Route table** — list of `RouteDef`s: `app.router.add_routes([web.get("/get", h)])`
3. **Decorators** — `RouteTableDef` container:

```python
routes = web.RouteTableDef()

@routes.get("/get")
async def handle_get(request): ...

@routes.view("/view")
class MyView(web.View): ...

app.add_routes(routes)
```

Internally the router (`app.router`, a `UrlDispatcher`) is a list of **resources**; a resource is a URL match, and each resource holds one **route** per HTTP method. Adding routes for the same path merges into one resource regardless of order.

```python
app.add_routes([web.get("/a", g1), web.post("/a", p1)])  # one resource, two routes
```

- Inspect: `app.router.resources()`, `app.router.named_resources()`.
- Wildcard method: `web.route("*", "/path", handler)` serves any method; check `request.method` inside.
- GET routes accept `HEAD` automatically; `web.get("/", handler, allow_head=False)` denies HEAD with 405.

## Variable paths

`{identifier}` parts default to regex `[^{}/]+`; custom: `{identifier:regex}`.

```python
app.add_routes([web.get("/{name}", variable_handler)])

async def variable_handler(request):
    return web.Response(text=request.match_info["name"])

# custom regex (URL is percent-encoded when matched)
app.add_routes([web.get(r"/{name:\\d+}", handler)])
```

## Named routes and URL reversing

Give a route a `name`, then build URLs:

```python
@routes.get("/root", name="root")
async def handler(request): ...

url = request.app.router["root"].url_for().with_query({"a": "b"})

app.router.add_resource("/{user}/info", name="user-info")
url = request.app.router["user-info"].url_for(user="john_doe")
```

For sub-applications, use the **sub-app's** router so the prefix is included.

## Class-based views

Subclass `web.View` and implement `get(self)`, `post(self)`, etc. The request is `self.request`. Unimplemented methods → 405.

```python
class MyView(web.View):
    async def get(self):
        return web.Response(text="hi")

app.add_routes([web.view("/path", MyView)])
# or with a decorator table:
# @routes.view("/path")
```

## Static files

```python
app.add_routes([web.static("/prefix", path_to_folder)])
```

Options: `show_index=True` (directory listing instead of 403), `append_version=True` (cache busting hash), `follow_symlinks=True` (**security risk** — allows symlink escape; dev-only). Prefer a reverse proxy (nginx/CDN) for production static assets.

## Sub-applications

Mount a fully separate `Application` under a prefix:

```python
admin = web.Application()
admin.add_routes([web.get("/resource", handler, name="res")])
app.add_subapp("/admin/", admin)
```

- Middlewares from the top app run **first**, then the sub-app's; the `on_response_prepare` signal fires for both.
- `on_startup`/`on_shutdown`/`on_cleanup` are delivered to all sub-apps; the argument is the **sub-app** instance, not the top-level app.
- Unlimited nesting depth.
- URL reversing must use the sub-app's router: `admin.router["res"].url_for()` → `URL("/admin/resource")`.
- Per-sub-app config lookup from any nested handler: `request.config_dict[my_key]` (sub-app → parents).
