# Security & Containerization

## Security Model

Pi runs with the permissions of the user account that starts it. It treats files writable by that user as inside the same local trust boundary.

### Project Trust

Project trust controls whether pi loads project-local settings, resources, packages, and extensions. It is not a sandbox.

Pi considers a project to have resources requiring trust when it finds:
- `.pi/settings.json`
- `.pi/extensions`, `.pi/skills`, `.pi/prompts`, `.pi/themes`
- `.pi/SYSTEM.md` or `.pi/APPEND_SYSTEM.md`
- project `.agents/skills`

A bare `.pi` directory does not count.

On interactive startup, pi follows `defaultProjectTrust` from global settings. Default is `"ask"`. Saved decisions stored in `~/.pi/agent/trust.json`.

Use `/trust` to save a decision for future sessions. Use `--approve`/`--no-approve` for one-run override.

Non-interactive modes use `defaultProjectTrust`: `"ask"` and `"never"` ignore project resources, `"always"` trusts them.

### No Built-in Sandbox

Pi does not include a built-in sandbox. Built-in tools can read, write, edit files, and run shell commands with full user permissions. Extensions run with the same permissions.

Prompt injection from repository files, comments, documentation, context files, or build output is expected local-agent risk.

## Containerization

Three patterns for isolation:

| Pattern | What is isolated | Best for |
|---------|-----------------|----------|
| Gondolin extension | Built-in tools and `!` commands | Local micro-VM, auth on host |
| Plain Docker | Whole `pi` process | Simple local isolation |
| OpenShell | Whole `pi` process | Policy-controlled sandbox |

### Gondolin

[Gondolin](https://github.com/earendil-works/gondolin) is a local Linux micro-VM. Use the example extension when you want `pi` on the host but all built-in tools routed into the VM.

```bash
cp -R packages/coding-agent/examples/extensions/gondolin ~/.pi/agent/extensions/gondolin
cd ~/.pi/agent/extensions/gondolin
npm install --ignore-scripts

cd /path/to/project
pi -e ~/.pi/agent/extensions/gondolin
```

Mounts host cwd at `/workspace` in the VM. Overrides `read`, `write`, `edit`, `bash`, `grep`, `find`, `ls`. User `!` commands routed into VM.

Requirements: Node.js >= 23.6.0, QEMU.

### Plain Docker

```dockerfile
FROM node:24-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends bash ca-certificates git ripgrep && rm -rf /var/lib/apt/lists/*
RUN npm install -g --ignore-scripts @earendil-works/pi-coding-agent
WORKDIR /workspace
ENTRYPOINT ["pi"]
```

```bash
docker build -t pi-sandbox -f Dockerfile.pi .

docker run --rm -it \
  -e ANTHROPIC_API_KEY \
  -v "$PWD:/workspace" \
  -v pi-agent-home:/root/.pi/agent \
  pi-sandbox
```

Mounting host `~/.pi/agent` exposes host auth and session files. Use a named volume for container-local settings.

### OpenShell

[NVIDIA OpenShell](https://docs.nvidia.com/openshell/about/overview) for policy-controlled sandbox with filesystem, process, network, credential, and inference controls.

```bash
openshell gateway add <gateway-url> --name <name>
openshell gateway select <name>

openshell sandbox create --name pi-sandbox --from pi -- pi
```

For remote gateways, use upload/download commands:

```bash
openshell sandbox upload pi-sandbox ./repo /workspace
openshell sandbox download pi-sandbox /workspace/repo ./repo-out
```

## Best Practices

- Mount only workspace paths the agent should access
- Avoid mounting host `~/.pi/agent` unless the container should access host sessions/credentials
- Pass minimum required API keys or use short-lived credentials
- Restrict network access when the task does not need it
- Review diffs and outputs before copying results back to trusted systems
- Use read-only mounts or copy files in/out when stronger protection is needed
