# 06 — Array Manipulation

## Joining Arrays

### `np.concatenate` / `np.concat`

```python
np.concatenate([a, b], axis=0)     # stack along existing axis
np.concat([a, b], axis=1)          # alias (Array API compatible)
```

All arrays must have the same shape except in the concatenation axis.

### `np.stack`

Creates a new axis and stacks arrays along it:

```python
np.stack([a, b], axis=0)           # new first axis
np.stack([a, b], axis=-1)          # new last axis
```

All arrays must have exactly the same shape.

### Convenience stacking functions

```python
np.vstack((a, b))     # np.concatenate along axis=0 (row stack)
np.hstack((a, b))     # np.concatenate along axis=1 (col stack)
np.dstack((a, b))     # concatenate along third axis (depth)
np.column_stack((a, b))  # 1D→columns, 2D→axis=1
```

### `np.block`

Compose arrays from nested lists:

```python
np.block([[A, B],
          [C, D]])
```

Supports mixing scalars, 1D, and ND arrays. Automatically broadcasts and concatenates.

## Splitting Arrays

```python
np.split(a, 3, axis=0)              # split into 3 equal parts
np.array_split(a, 3, axis=0)        # allows unequal parts
np.vsplit(a, 3)                     # split along axis=0
np.hsplit(a, 3)                     # split along axis=1
np.dsplit(a, 3)                     # split along axis=2
np.unstack(a, axis=0)               # reverse of stack
```

`split` requires equal-sized chunks. `array_split` allows uneven splits.

## Transposing and Swapping Axes

```python
a.T                         # transpose (reverse all axes)
np.transpose(a)             # same as .T
np.transpose(a, (2, 0, 1)) # permute axes: axis 2→0, 0→1, 1→2
np.swapaxes(a, 0, 1)       # swap two axes
np.moveaxis(a, 0, -1)      # move axis 0 to last position
np.rollaxis(a, 0, -1)      # roll axis 0 to position -1
```

## Padding and Repeating

### Padding

```python
np.pad(a, 2)                           # pad all edges by 2
np.pad(a, ((1, 2), (3, 4)))            # per-axis: (before, after)
np.pad(a, 2, mode='edge')              # extend edge values
np.pad(a, 2, mode='reflect')           # mirror the array
np.pad(a, 2, mode='wrap')              # wrap around
np.pad(a, 2, mode='constant', constant_values=0)  # fill with value
np.pad(a, 2, mode='linear_ramp', end_values=0)    # ramp to edge values
```

### Repeating and tiling

```python
np.repeat(a, 3)               # repeat each element 3 times
np.repeat(a, 3, axis=0)       # repeat rows 3 times
np.tile(a, (2, 3))            # tile the whole array 2×3 times
```

## Reshaping Operations

### Flatten vs ravel vs reshape

```python
a.flatten()           # always returns a copy
np.ravel(a)           # returns view when possible, copy otherwise
a.reshape(-1)         # preferred for guaranteed view (when memory allows)
a.reshape(new_shape)  # reshape to new shape; -1 infers one dimension
```

### Adding/removing dimensions

```python
np.expand_dims(a, axis=0)      # insert size-1 dimension
np.squeeze(a)                  # remove all size-1 dimensions
np.squeeze(a, axis=(0, 2))     # remove specific dimensions
a[:, np.newaxis]               # add dimension via indexing
```

### Broadcasting to explicit shape

```python
np.broadcast_to(a, (4, 3))     # broadcast a to shape (4, 3) — read-only view
np.broadcast_arrays(a, b)      # broadcast multiple arrays to common shape
```

## Copying and Moving Data

```python
a.copy()                       # deep copy
np.copyto(dst, src)            # in-place copy (supports where= mask)
np.copyto(dst, src, where=mask)# conditional copy
```

### Memory sharing checks

```python
np.shares_memory(a, b)         # do a and b share memory?
np.may_share_memory(a, b)      # might share (faster, may have false positives)
a.base is not None             # is a a view of another array?
```

## Tiling Patterns

```python
# Create checkerboard pattern
checker = np.tile(np.array([[0, 1], [1, 0]]), (rows//2, cols//2))

# Repeat each row
repeated = np.repeat(a, repeats=[1, 3, 2], axis=0)

# Broadcast a column vector to fill a matrix
filled = np.broadcast_to(a[:, None], (a.shape[0], n_cols))
```

## Diagonal Operations

```python
np.diag(v)                     # create diagonal matrix from 1D array
np.diag(a)                     # extract diagonal of 2D array
np.diag(a, k=1)                # extract/set k-th off-diagonal
np.diagonal(a)                 # view of diagonal (no copy)
np.diagonal(a, offset=1)       # off-diagonal view
np.fill_diagonal(a, val)       # fill diagonal in-place
```

## Clip and Sign

```python
np.clip(a, min_val, max_val)   # clip values to range
np.sign(a)                     # sign of each element (-1, 0, +1)
np.abs(a)                      # absolute value
np.negative(a)                 # negate
```
