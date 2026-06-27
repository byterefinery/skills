# scipy.constants Reference

Physical and mathematical constants, units, SI prefixes, and the CODATA constants database.

## Table of Contents

- [Mathematical Constants](#mathematical-constants)
- [Physical Constants (Key)](#physical-constants-key)
- [Constants Database](#constants-database)
- [Units](#units)
- [SI Prefixes](#si-prefixes)
- [Physical Quantities as Units](#physical-quantities-as-units)
- [Utility Functions](#utility-functions)

## Mathematical Constants

| Name | Value | Description |
|---|---|---|
| `pi` | 3.14159... | Pi (π) |
| `e` | 2.71828... | Euler's number (note: also elementary charge) |
| `golden` / `golden_ratio` | 1.61803... | Golden ratio (φ) |
| `inf` | ∞ | Positive infinity |
| `nan` | NaN | Not a number |
| `degree` | π/180 | One degree in radians |
| `Euler` / `EulerGamma` | 0.57721... | Euler-Mascheroni constant (γ) |

```python
from scipy.constants import pi, golden, Euler

print(pi)        # 3.141592653589793
print(golden)    # 1.618033988749895
print(Euler)     # 0.5772156649015329
```

## Physical Constants (Key)

All values are in SI units. Each constant has short and long name aliases.

| Short | Long | Quantity | SI Units |
|---|---|---|---|
| `c` | `speed_of_light` | Speed of light in vacuum | m/s |
| `h` | `Planck` | Planck constant | J·s |
| `hbar` | — | Reduced Planck constant (ℏ = h/2π) | J·s |
| `G` | `gravitational_constant` | Gravitational constant | m³/(kg·s²) |
| `g` | — | Standard acceleration of gravity | m/s² |
| `e` | `elementary_charge` | Elementary charge | C |
| `mu_0` | — | Magnetic constant (μ₀) | N/A² |
| `epsilon_0` | — | Electric constant / vacuum permittivity (ε₀) | F/m |
| `R` | `gas_constant` | Molar gas constant | J/(mol·K) |
| `N_A` | `Avogadro` | Avogadro constant | mol⁻¹ |
| `k` | `Boltzmann` | Boltzmann constant | J/K |
| `sigma` | `Stefan_Boltzmann` | Stefan-Boltzmann constant | W/(m²·K⁴) |
| `alpha` | `fine_structure` | Fine-structure constant | (dimensionless) |
| `Rydberg` | — | Rydberg constant | m⁻¹ |
| `m_e` | `electron_mass` | Electron mass | kg |
| `m_p` | `proton_mass` | Proton mass | kg |
| `m_n` | `neutron_mass` | Neutron mass | kg |
| `Wien` | — | Wien displacement constant | m·K |
| `a_0` | `physical_constants['Bohr radius']` | Bohr radius | m |

```python
from scipy.constants import c, h, hbar, G, k, N_A, m_e

print(f"Speed of light: {c:.3e} m/s")
print(f"Planck constant: {h:.3e} J·s")
print(f"Boltzmann constant: {k:.3e} J/K")
```

## Constants Database

### `physical_constants`

Dictionary of all physical constants. Each entry is `(value, unit_string, uncertainty)`.

```python
from scipy.constants import physical_constants

# Access by name
value, unit, uncertainty = physical_constants['speed of light in vacuum']
print(f"c = {value} {unit} ± {uncertainty}")

# List all constants
for name, (val, unit, unc) in sorted(physical_constants.items()):
    print(f"{name}: {val:.6e} {unit}")
```

### `value(number)`

Look up a constant by its CODATA number. Returns the value.

```python
from scipy.constants import value

# CODATA constant 2 = speed of light
c = value(2)
print(c)  # 299792458.0 (exact)
```

### `constant(name)`

Look up a constant by name string. Returns `(value, unit, uncertainty)`.

```python
from scipy.constants import constant

val, unit, unc = constant('electron mass')
print(f"m_e = {val} {unit}")
```

## Units

SI and common units are available as conversion factors to SI base units.

### Base and derived units

| Unit | Symbol(s) | Conversion |
|---|---|---|
| meter | `m` | 1 (base unit) |
| kilogram | `kg` | 1 (base unit) |
| second | `s` | 1 (base unit) |
| ampere | `A` | 1 (base unit) |
| kelvin | `K` | 1 (base unit) |
| mole | `mole` | 1 (base unit) |
| candela | `candela` | 1 (base unit) |
| hertz | `Hz` | 1/s |
| newton | `N` | kg·m/s² |
| pascal | `Pa` | N/m² |
| joule | `J` | N·m |
| watt | `W` | J/s |
| volt | `V` | W/A |
| coulomb | `C` | A·s |
| farad | `F` | C/V |
| ohm | `ohm` | V/A |
| siemens | `S` | A/V |
| weber | `Wb` | V·s |
| tesla | `T` | Wb/m² |
| henry | `H` | Wb/A |

```python
from scipy.constants import Hz, N, Pa, J, W, V, C

# Convert between units
energy_joules = 100 * J
power_watts = energy_joules / 5  # 20 W
```

### Common non-SI units

| Unit | Symbol(s) | Approximate SI Equivalent |
|---|---|---|
| atmosphere | `atm` | 101325 Pa |
| torr | `torr` | 133.322 Pa |
| bar | `bar` | 10⁵ Pa |
| angstrom | `angstrom` / `Å` | 10⁻¹⁰ m |
| nanometer | `nm` | 10⁻⁹ m |
| micrometer | `um` / `micron` | 10⁻⁶ m |
| millimeter | `mm` | 10⁻³ m |
| kilometer | `km` | 10³ m |
| light_year | `light_year` | ~9.461×10¹⁵ m |
| astronomical_unit | `astronomical_unit` / `au` | ~1.496×10¹¹ m |
| parsec | `parsec` | ~3.086×10¹⁶ m |
| electron_volt | `eV` | 1.602×10⁻¹⁹ J |
| keV, MeV, GeV, TeV | `keV`, `MeV`, etc. | ×10³, ×10⁶, etc. |
| calorie | `calorie` / `cal` | 4.184 J |
| kcal | `kcal` | 4184 J |
| watt_hour | `watt_hour` / `Wh` | 3600 J |
| hour | `hour` | 3600 s |
| day | `day` | 86400 s |
| year | `year` | 365.25 × 86400 s |
| minute | `minute` | 60 s |
| barn | `barn` | 10⁻²⁸ m² |

```python
from scipy.constants import eV, nm, angstrom, atm, kcal

# Energy conversions
energy_eV = 13.6 * eV      # Hydrogen ionization energy
energy_J = energy_eV        # Already in joules (eV converts to J)

# Length conversions
wavelength = 500 * nm       # 500 nanometers
bond_length = 1.54 * angstrom  # C-C bond length
```

## SI Prefixes

All standard SI prefixes are available:

| Prefix | Factor | Names |
|---|---|---|
| yotta | 10²⁴ | `yotta`, `Y` |
| zetta | 10²¹ | `zetta`, `Z` |
| exa | 10¹⁸ | `exa`, `E` |
| peta | 10¹⁵ | `peta`, `P` |
| tera | 10¹² | `tera`, `T` |
| giga | 10⁹ | `giga`, `G` |
| mega | 10⁶ | `mega`, `M` |
| kilo | 10³ | `kilo`, `k` |
| hecto | 10² | `hecto`, `h` |
| deca | 10¹ | `deca`, `da` |
| deci | 10⁻¹ | `deci`, `d` |
| centi | 10⁻² | `centi`, `c` |
| milli | 10⁻³ | `milli`, `m` |
| micro | 10⁻⁶ | `micro`, `u` |
| nano | 10⁻⁹ | `nano`, `n` |
| pico | 10⁻¹² | `pico`, `p` |
| femto | 10⁻¹⁵ | `femto`, `f` |
| atto | 10⁻¹⁸ | `atto`, `a` |
| zepto | 10⁻²¹ | `zepto`, `z` |
| yocto | 10⁻²⁴ | `yocto`, `y` |

### Binary prefixes

| Prefix | Factor | Names |
|---|---|---|
| kibi | 2¹⁰ = 1024 | `kibi`, `Ki` |
| mebi | 2²⁰ | `mebi`, `Mi` |
| gibi | 2³⁰ | `gibi`, `Gi` |
| tebi | 2⁴⁰ | `tebi`, `Ti` |
| pebi | 2⁵⁰ | `pebi`, `Pi` |
| exbi | 2⁶⁰ | `exbi`, `Ei` |
| zebi | 2⁷⁰ | `zebi`, `Zi` |
| yobi | 2⁸⁰ | `yobi`, `Yi` |

```python
from scipy.constants import kilo, mega, giga, milli, micro, nano

# Use prefixes directly
resistance = 4.7 * kilo          # 4700 ohms
frequency = 2.4 * giga           # 2.4 GHz
capacitance = 100 * nano         # 100 nF
time = 5 * micro                 # 5 microseconds
```

## Physical Quantities as Units

| Category | Available Units |
|---|---|
| Mass | `amu` (atomic mass unit), `Dalton`, `electron_mass`, `proton_mass`, `neutron_mass` |
| Angle | `degree`, `radian`, `arcminute`, `arcsecond`, `steradian`, `turn` |
| Time | `attosecond`, `femtosecond`, `picosecond`, `nanosecond`, `microsecond`, `millisecond`, `second`, `minute`, `hour`, `day`, `year`, `tropical_year`, `sidereal_year`, `Julian_year` |
| Length | `angstrom`, `nm`, `um`, `mm`, `cm`, `m`, `km`, `mile`, `yard`, `foot`, `inch`, `light_year`, `astronomical_unit`, `parsec` |
| Pressure | `atm`, `torr`, `bar`, `Pa`, `psi` |
| Area | `barn`, `acre`, `hectare` |
| Volume | `liter`, `milliliter`, `gallon`, `quart`, `pint`, `cup`, `fluid_ounce`, `tablespoon`, `teaspoon` |
| Speed | `c` (speed of light), `knot`, `mach` |
| Temperature | `degC` (°C offset), `degF` (°F offset), `K` (kelvin) |
| Energy | `J`, `eV`, `calorie`, `kcal`, `watt_hour`, `electron_volt`, `rydberg` |
| Power | `W`, `hp` (horsepower) |
| Force | `N`, `dyne`, `pound_force` |
| Optics | `refractive_index_of_vacuum` (= 1) |

## Utility Functions

| Function | Description |
|---|---|
| `value(n)` | Look up CODATA constant by number |
| `constant(name)` | Look up constant by name string |
| `find(name)` | Search constants database (returns matching entries) |
| `physical_constants` | Full dictionary of physical constants |
| `codata_value_dict` | CODATA values as dictionary |

```python
from scipy.constants import find

# Search for constants
results = find('electron')
for name, (val, unit, unc) in results.items():
    print(f"{name}: {val:.6e} {unit}")
```
