# Physics Modules Reference

## Quantum Mechanics

### Bra-ket notation and Hilbert spaces

```python
from sympy.physics.quantum import Ket, Bra, InnerProduct, OuterProduct
from sympy.physics.quantum import Commutator, Anticommutator
from sympy import symbols

# Kets and bras
psi = Ket('|ψ⟩')
phi = Ket('|φ⟩')
psi_dual = Bra('ψ')

# Inner/outer products
InnerProduct(psi_dual, phi)     # ⟨ψ|φ⟩
OuterProduct(phi, psi_dual)     # |φ⟩⟨ψ|

# Commutators
from sympy.physics.quantum.operator import Operator
A = Operator('A')
B = Operator('B')
Commutator(A, B)               # [A, B]
Anticommutator(A, B)           # {A, B}
```

### Spin and Pauli matrices

```python
from sympy.physics.paulialgebra import Pauli, pauli, sigma
from sympy import I

# Pauli matrices
sigma_x, sigma_y, sigma_z = pauli(1), pauli(2), pauli(3)
# or: sigma[1], sigma[2], sigma[3]

# Properties
sigma_x**2                    # Identity
sigma_x * sigma_y             # I*sigma_z
```

## Mechanics (Rigid Body Dynamics)

### Symbolic dynamics with Lagrange/Kane methods

```python
from sympy.physics.mechanics import (
    ReferenceFrame, Point, Particle, RigidBody,
    inertia, dyadic, KanesMethod, LagrangesMethod
)
from sympy import symbols, sin, cos

# Create reference frames
N = ReferenceFrame('N')
body_frame = ReferenceFrame('B')

# Orientation
q1 = symbols('q1', function_of=[symbols('t')])
body_frame.orient(N, 'Axis', (q1, N.z))

# Points and velocities
O = Point('O')
P = O.locatenew('P', L*cos(q1)*N.x + L*sin(q1)*N.y)
P.v2pt_theorem(O, N, body_frame)

# Particles and rigid bodies
I = inertia(body_frame, Ixx, Iyy, Izz)
body = RigidBody('body', P, body_frame, m, I)

# Kane's method
KanesMethod(N, [q1], [u1], kind='Kane')
```

### Lagrange's equations

```python
from sympy.physics.mechanics import LagrangesMethod

# Define Lagrangian L = T - V
Lagrangian = T - V
lm = LagrangesMethod(Lagrangian, [q1, q2], frame=N)
lm.form_lagranges()
lm.linearize()
```

## Units and Dimensions

```python
from sympy.physics.units import (
    meter, second, kilogram, gram, ampere,
    volt, ohm, watt, joule, newton, hertz,
    speed_of_light, Planck, gravitational_constant
)
from sympy.physics.units import dimensionless, convert_to
from sympy import symbols

# Dimensional analysis
length = 5 * meter
time = 2 * second
velocity = length / time
velocity.check(meter / second)   # True

# Unit conversion
convert_to(1000 * gram, kilogram)    # 1*kilogram
convert_to(1 * watt, newton*meter/second)

# Physical constants
speed_of_light          # c
Planck                  # ℏ (reduced Planck constant)
gravitational_constant  # G
```

## Hydrogen Atom

```python
from sympy.physics.hydrogen import R_nl, E_n, Ynl
from sympy import symbols

n, l, m = symbols('n l m', integer=True)
r, theta, phi = symbols('r theta phi')

# Radial wave function
R_nl(2, 0, r)          # R_{2,0}(r)

# Energy levels
E_n(1)                  # -13.6 eV (ground state)
```

## Simple Harmonic Oscillator

```python
from sympy.physics.sho import psi_n, psi_n_prime, ho
from sympy import symbols

n = symbols('n', integer=True)
x = symbols('x')
psi_n(n, x)             # nth eigenstate wave function
```

## Wigner D-matrices

```python
from sympy.physics.wigner import wigner_d, wigner_D, wigner_3j, wigner_6j, wigner_9j
from sympy import symbols

j, m1, m2 = symbols('j m1 m2')
theta = symbols('theta')

wigner_d(j, m1, m2, theta)    # d^j_{m1,m2}(θ)
wigner_3j(j1, j2, j3, m1, m2, m3)
wigner_6j(j1, j2, j3, j4, j5, j6)
```

## Tensor Algebra

### Indexed tensors

```python
from sympy import IndexedBase, Idx, Sum
from sympy.tensor import tensorproduct, tensorcontraction

# Indexed base
A = IndexedBase('A')
i, j = Idx('i', 3), Idx('j', 3)
A[i, j]                    # A_{i,j}

# Einstein summation
expr = A[i, j] * B[j, i]   # implicit sum over j
```

### N-dimensional arrays

```python
from sympy import MutableDenseNDimArray, tensorcontraction, tensorproduct

# Create ND array
arr = MutableDenseNDimArray([1, 2, 3, 4], (2, 2))
tensorproduct(arr, arr)
tensorcontraction(tensorproduct(arr, arr), (1, 2))
```

## Control Systems

```python
from sympy.physics.control import transfer_function, state_space
from sympy import symbols, laplace_transform

# Transfer function analysis
s = symbols('s')
H = 1 / (s**2 + 2*s + 1)
```

## Gotchas

- **`physics.quantum` is a framework, not a solver** — it provides symbolic notation but you must implement the physics yourself.
- **Mechanics module has steep learning curve** — frames, points, and velocities must be set up carefully. Follow the tutorial examples closely.
- **Units require explicit multiplication** — `5 * meter`, not `meter(5)`.
- **`convert_to()` may not handle all unit combinations** — it works best within the same dimension system.
- **Wigner symbols are computationally expensive** — large j values slow down significantly.
- **Physics modules are imported separately** — they are not in the main `from sympy import *`. Use explicit imports from `sympy.physics.*`.
