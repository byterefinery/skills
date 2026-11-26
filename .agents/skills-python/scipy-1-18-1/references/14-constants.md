# scipy.constants Reference (1.18.1)

Physical and mathematical constants, units, and the CODATA constants database (2022 recommended values).

## Table of Contents

- [Mathematical Constants](#mathematical-constants)
- [Physical Constants (Key)](#physical-constants-key)
- [Constants Database](#constants-database)
- [Units](#units)
- [SI and Binary Prefixes](#si-and-binary-prefixes)

## Mathematical Constants

| Name | Value | Description |
|---|---|---|
| `pi` | 3.14159... | Pi (π) |
| `golden` / `golden_ratio` | 1.61803... | Golden ratio (φ) |

Note: there is no bare `e` for Euler's number (that is `math.e`) — in `scipy.constants`, `e` is the **elementary charge**.

```python
from scipy.constants import pi, golden
print(pi)        # 3.141592653589793
print(golden)    # 1.618033988749895
```

## Physical Constants (Key)

All values are in SI units. Each constant has a short and a long name alias (from the module docstring):

| Short | Long | Quantity | SI Units |
|---|---|---|---|
| `c` | `speed_of_light` | Speed of light in vacuum | m/s |
| `h` | `Planck` | Planck constant | J·s |
| `hbar` | — | Reduced Planck constant (ℏ = h/2π) | J·s |
| `G` | `gravitational_constant` | Newtonian gravitational constant | m³/(kg·s²) |
| `g` | — | Standard acceleration of gravity | m/s² |
| `e` | `elementary_charge` | Elementary charge | C |
| `mu_0` | — | Magnetic constant (μ₀) | N/A² |
| `epsilon_0` | — | Electric constant / vacuum permittivity (ε₀) | F/m |
| `R` | `gas_constant` | Molar gas constant | J/(mol·K) |
| `N_A` | `Avogadro` | Avogadro constant | mol⁻¹ |
| `k` | `Boltzmann` | Boltzmann constant | J/K |
| `sigma` | `Stefan_Boltzmann` | Stefan-Boltzmann constant | W/(m²·K⁴) |
| `alpha` | `fine_structure` | Fine-structure constant | (dimensionless) |
| `Wien` | — | Wien wavelength displacement constant | m·K |
| `Rydberg` | — | Rydberg constant | m⁻¹ |
| `m_e` | `electron_mass` | Electron mass | kg |
| `m_p` | `proton_mass` | Proton mass | kg |
| `m_n` | `neutron_mass` | Neutron mass | kg |

```python
from scipy.constants import c, h, k, N_A, m_e
print(f"Speed of light: {c:.3e} m/s")
print(f"Planck constant: {h:.3e} J·s")
```

## Constants Database

`scipy.constants` contains the **2022 CODATA** recommended values database.

### `physical_constants`

Dictionary: `physical_constants[name] = (value, unit, uncertainty)` — uncertainty `0.0` means the CODATA value is exact.

```python
from scipy.constants import physical_constants

value, unit, uncertainty = physical_constants['speed of light in vacuum']
print(f"c = {value} {unit} ± {uncertainty}")
```

### Lookup functions

| Function | Description |
|---|---|
| `value(key)` | Value in `physical_constants` indexed by key |
| `unit(key)` | Unit string in `physical_constants` indexed by key |
| `precision(key)` | Relative precision in `physical_constants` indexed by key |
| `find(name)` | Return list of `physical_constants` keys containing the string |
| `ConstantWarning` | Warning when a constant is not in the newest CODATA data set |

```python
from scipy.constants import find, value

results = find('electron')     # search the constants database
c = value(2)                   # look up by CODATA number (2 = speed of light)
```

## Units

Conversion factors to SI base units, defined in the module (see the "Units" section of the module docstring). Highlights of what exists:

- **Pressure/energy/heat:** `atm`/`atmosphere`, `torr`, `mmHg`, `bar`, `calorie`/`calorie_IT`/`calorie_th`, `Btu`/`Btu_IT`/`Btu_th`, `erg`, `eV`/`electron_volt`
- **Length:** `angstrom`, `astronomical_unit`/`au`, `fermi`, `foot`, `inch`, `light_year`, `mile`, `mil`, `nautical_mile`, `parsec`, `point`/`pt`, `survey_foot`, `survey_mile`, `yard`, `micron`
- **Mass:** `gram`, `atomic_mass`/`u`/`m_u`, `pound`/`lb`, `ounce`/`oz`, `grain`, `carat`, `stone`, `slug`, `kilogram_force`/`kgf`, tons (`metric_ton`, `short_ton`, `long_ton`, `ton_TNT`)
- **Volume:** `liter`/`litre`, `gallon`/`gallon_US`/`gallon_imp`, `barrel`/`bbl`, `fluid_ounce`/`fluid_ounce_US`/`fluid_ounce_imp`
- **Time:** `minute`, `hour`, `day`, `week`, `year`, `Julian_year`
- **Speed:** `kmh`, `mph`, `knot`, `mach`, `speed_of_sound`
- **Force/power:** `dyne`/`dyn`, `pound_force`/`lbf`, `horsepower`/`hp`
- **Angle:** `degree`, `arcmin`/`arcminute`, `arcsec`/`arcsecond`
- **Temperature helpers:** `zero_Celsius`, `degree_Fahrenheit`, `convert_temperature(t, dt, input_unit, output_unit)`

There are no bare SI unit symbols (no `nm`, `keV`, `ohm`, `steradian`, `quart`, `barn`, `kcal`, `watt_hour`, `degC`/`degF`) — use the named units above or plain factors (`500e-9` m for 500 nm).

## SI and Binary Prefixes

SI prefixes (all available as multipliers): `quetta` (10³⁰), `ronna` (10²⁷), `yotta`, `zetta`, `exa`, `peta`, `tera`, `giga`, `mega`, `kilo`, `hecto`, `deka`, `deci`, `centi`, `milli`, `micro`, `nano`, `pico`, `femto`, `atto`, `zepto`, `yocto`, `ronto` (10⁻²⁷), `quecto` (10⁻³⁰).

Binary prefixes: `kibi` (2¹⁰), `mebi`, `gibi`, `tebi`, `pebi`, `exbi`, `zebi`, `yobi`.

```python
from scipy.constants import kilo, giga, micro, eV

resistance = 4.7 * kilo          # 4700 (unit-less multiplier)
frequency = 2.4 * giga           # 2.4 × 10⁹
time = 5 * micro                 # 5 × 10⁻⁶
energy = 13.6 * eV               # joules (eV converts to J)
```
