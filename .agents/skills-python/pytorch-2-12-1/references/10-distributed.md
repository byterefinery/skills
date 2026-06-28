# Distributed Training Reference

## Initialization

### `torch.distributed.init_process_group`

```python
import torch.distributed as dist

dist.init_process_group(
    backend="nccl",       # "nccl" (CUDA), "gloo" (CPU), "hccl" (Huawei)
    rank=rank,            # process rank (0 to world_size-1)
    world_size=world_size,# total number of processes
)
```

### Launch Utilities

```python
# torchrun (recommended)
torchrun --nproc_per_node=4 --nnodes=1 train.py

# mpirun
mpirun -np 4 python train.py

# Manual (not recommended for production)
# Each process calls init_process_group with correct rank/world_size
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `MASTER_ADDR` | IP address of rank 0 node |
| `MASTER_PORT` | Port for communication |
| `RANK` | Global process rank |
| `WORLD_SIZE` | Total number of processes |
| `LOCAL_RANK` | Rank within the node |
| `LOCAL_WORLD_SIZE` | Processes per node |

`torchrun` sets these automatically.

## DDP (DistributedDataParallel)

### Basic Usage

```python
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

# Setup
dist.init_process_group("nccl")
local_rank = dist.get_rank()

# Move model to local GPU
model = Model().to(local_rank)

# Wrap with DDP
model = DDP(model, device_ids=[local_rank], output_device=local_rank)

# Training loop
for x, y in loader:
    x, y = x.to(local_rank), y.to(local_rank)
    output = model(x)
    loss = criterion(output, y)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

# Cleanup
dist.destroy_process_group()
```

### DDP Constructor

```python
DDP(
    module,
    device_ids=None,              # list of GPU ids (auto-detected if None)
    output_device=None,           # GPU for output
    broadcast_buffers=True,       # broadcast buffers from rank 0
    bucket_cap_mb=25,             # gradient bucket size
    find_unused_parameters=False, # True if forward doesn't use all params
    static_graph=False,           # True if computation graph is static
    gradient_as_bucket_view=False,# reuse bucket memory for gradients
    sparse_gradient_average=True, # average sparse gradients
)
```

**Rule:** Set `find_unused_parameters=True` only when needed (e.g., GANs where discriminator doesn't use generator params). It adds overhead.

### No Sync Context

```python
# Skip gradient synchronization (e.g., for validation inside training loop)
with model.no_sync():
    val_output = model(val_x)
    val_loss = criterion(val_output, val_y)
    # No allreduce — saves communication
```

## FSDP (FullyShardedDataParallel)

### Basic Usage

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import MixedPrecision, ShardingStrategy
from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy, transformer_auto_wrap_policy

# Mixed precision config
mp_policy = MixedPrecision(
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.bfloat16,
    buffer_dtype=torch.bfloat16,
)

# Auto-wrap policy
wrap_policy = size_based_auto_wrap_policy(min_num_params=100_000_000)

# Wrap model
model = FSDP(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,
    mixed_precision=mp_policy,
    auto_wrap_policy=wrap_policy,
    backward_prefetch=BackwardPrefetch.BACKWARD_PRE,
    limit_all_gathers=True,
)
```

### Sharding Strategies

| Strategy | Description |
|----------|-------------|
| `FULL_SHARD` | Shard parameters, gradients, and optimizer states |
| `SHARD_GRAD_OP` | Shard gradients and optimizer states only |
| `NO_SHARD` | No sharding (equivalent to DDP) |
| `_HYBRID_SHARD` | Shard within node, replicate across nodes |
| `_HYBRID_SHARD_ZERO2` | Hybrid with SHARD_GRAD_OP |

### FSDP Checklist

```python
from torch.distributed.fsdp import FullStateDictConfig, StateDictType

# Get full state dict for saving
with FSDP.state_dict_type(
    model,
    StateDictType.FULL_STATE_DICT,
    FullStateDictConfig(offload_to_cpu=True, rank0_only=True),
):
    state_dict = model.state_dict()
    if dist.get_rank() == 0:
        torch.save(state_dict, "model.pth")
```

## Collective Operations

### Point-to-Point

```python
# Send/Receive
dist.send(tensor, dst=1)
dist.recv(tensor, src=0)

# Non-blocking
work_send = dist.isend(tensor, dst=1)
work_recv = dist.irecv(tensor, src=0)
work_send.wait()
work_recv.wait()
```

### Group Collectives

```python
# All-reduce (sum across all processes)
dist.all_reduce(tensor, op=dist.ReduceOp.SUM)

# Broadcast (from root to all)
dist.broadcast(tensor, src=0)

# Gather (collect from all to root)
gathered = [torch.zeros_like(tensor) for _ in range(world_size)]
dist.gather(tensor, gathered, dst=0)

# All-gather (collect from all to all)
gathered = [torch.zeros_like(tensor) for _ in range(world_size)]
dist.all_gather(gathered, tensor)

# Reduce (reduce to root)
dist.reduce(tensor, dst=0, op=dist.ReduceOp.SUM)

# Reduce-scatter
output = torch.zeros(reduced_size, device="cuda")
dist.reduce_scatter(output, input_list, op=dist.ReduceOp.SUM)

# Barrier (synchronize all processes)
dist.barrier()
```

### Async Operations

```python
# Non-blocking all_reduce
work = dist.all_reduce(tensor, async_op=True)
# ... do other work ...
work.wait()
```

## Distributed Sampler

```python
from torch.utils.data import DistributedSampler, DataLoader

sampler = DistributedSampler(
    dataset,
    num_replicas=dist.get_world_size(),
    rank=dist.get_rank(),
    shuffle=True,
    seed=42,
)

loader = DataLoader(dataset, sampler=sampler, batch_size=32)

# Set epoch for different shuffles
for epoch in range(num_epochs):
    sampler.set_epoch(epoch)
    for batch in loader:
        ...
```

## RPC (Remote Procedure Call)

```python
import torch.distributed.rpc as rpc

# Initialize
rpc.init_rpc("worker1", rank=0, world_size=2)

# Define remote function
@rpc.functions.async_execution
def remote_forward(model, x):
    return model(x)

# Call remotely
future = rpc.rpc_async("worker2", remote_forward, args=(model, x))
result = future.wait()

# RRef (remote reference)
rref = rpc.RRef(model, owner="worker2")
output = rpc.rpc_sync("worker2", model.forward, args=(rref, x))

# Cleanup
rpc.shutdown()
```

## Distributed Optimizer

```python
from torch.distributed.optim import ZeroRedundancyOptimizer

# Shards optimizer states across processes
optimizer = ZeroRedundancyOptimizer(
    model.parameters(),
    optimizer_class=torch.optim.AdamW,
    lr=1e-3,
)
```

## Common Patterns

### Train with DDP

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DistributedSampler

def main():
    dist.init_process_group("nccl")
    rank = dist.get_rank()
    local_rank = int(os.environ["LOCAL_RANK"])

    model = Model().to(local_rank)
    model = DDP(model, device_ids=[local_rank])

    sampler = DistributedSampler(dataset, shuffle=True)
    loader = DataLoader(dataset, sampler=sampler, batch_size=32)

    optimizer = optim.AdamW(model.parameters(), lr=1e-3)

    for epoch in range(num_epochs):
        sampler.set_epoch(epoch)
        model.train()
        for x, y in loader:
            x, y = x.to(local_rank), y.to(local_rank)
            optimizer.zero_grad()
            loss = model(x, y)
            loss.backward()
            optimizer.step()

        # Save from rank 0 only
        if rank == 0:
            torch.save(model.module.state_dict(), f"model_epoch_{epoch}.pth")

    dist.destroy_process_group()
```

### Gradient Accumulation with DDP

```python
accum_steps = 4
for i, (x, y) in enumerate(loader):
    x, y = x.to(local_rank), y.to(local_rank)
    with model.no_sync() if (i + 1) % accum_steps != 0 else nullcontext():
        loss = model(x, y) / accum_steps
        loss.backward()

    if (i + 1) % accum_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

## Debugging

```python
# Check if NCCL is working
print(torch.cuda.nccl.version())

# Debug synchronization
dist.barrier()
print(f"Rank {dist.get_rank()} reached checkpoint")

# Hang detection
import os
os.environ["NCCL_DEBUG"] = "INFO"      # NCCL debug info
os.environ["TORCH_DISTRIBUTED_DEBUG"] = "DETAIL"  # PyTorch dist debug
```

## Gotchas

- **DDP requires same model on all ranks** — initialize model before wrapping with DDP.
- **`find_unused_parameters=True` adds overhead** — only use when forward doesn't use all parameters.
- **FSDP changes state_dict keys** — use `FSDP.state_dict_type()` context manager for saving/loading.
- **DistributedSampler requires `set_epoch()`** — call before each epoch for different shuffles.
- **NCCL requires GPU** — use `gloo` backend for CPU-only distributed training.
- **`dist.all_reduce` modifies in-place** — the tensor is updated directly.
- **Rank 0 only for I/O** — only rank 0 should save models or write logs to avoid file conflicts.
- **`destroy_process_group()` at exit** — always clean up to avoid hanging processes.
