# Signal Math

Tone.js provides signal-level math operations for audio-rate computation. All math nodes extend `Signal` and can be chained.

## Add

Add two signals together.

```js
const add = new Tone.Add(10);
signal1.connect(add);
// output = signal1 + 10
```

```js
const add = new Tone.Add();
signal1.connect(add);
signal2.connect(add.input);
// output = signal1 + signal2
```

## Subtract

Subtract one signal from another.

```js
const sub = new Tone.Subtract(5);
signal1.connect(sub);
// output = signal1 - 5
```

## Multiply

Multiply a signal by a value.

```js
const mul = new Tone.Multiply(2);
signal1.connect(mul);
// output = signal1 * 2
```

## Divide

Divide a signal by a value.

```js
const div = new Tone.Multiply(0.5);  // use Multiply with reciprocal
```

Note: There is no `Tone.Divide`; use `Multiply(1/x)` instead.

## Pow

Raise a signal to a power.

```js
const pow = new Tone.Pow(2);
signal.connect(pow);
// output = signal ^ 2
```

## Negate

Invert the sign of a signal.

```js
const neg = new Tone.Negate();
signal.connect(neg);
// output = -signal
```

## Abs

Absolute value of a signal.

```js
const abs = new Tone.Abs();
signal.connect(abs);
// output = |signal|
```

## Scale

Linearly scale a signal from one range to another.

```js
const scale = new Tone.Scale(0, 1000);
// Input 0-1 → Output 0-1000
lfo.connect(scale);
scale.connect(filter.frequency);
```

```js
const scale = new Tone.Scale({
  min: 200,
  max: 4000,
});
```

## ScaleExp

Exponential scaling from one range to another.

```js
const scaleExp = new Tone.ScaleExp(100, 10000);
// Input 0-1 → Output 100-10000 (exponential)
lfo.connect(scaleExp);
scaleExp.connect(filter.frequency);
```

## AudioToGain

Convert audio range (-1 to 1) to gain range (0 to 1).

```js
const a2g = new Tone.AudioToGain();
oscillator.connect(a2g);
a2g.connect(gain.gain);
```

## GainToAudio

Convert gain range (0 to 1) to audio range (-1 to 1).

```js
const g2a = new Tone.GainToAudio();
```

## GreaterThan

Output 1 if signal is greater than a threshold, 0 otherwise.

```js
const gt = new Tone.GreaterThan(0);
signal.connect(gt);
// output = 1 if signal > 0, else 0
```

## GreaterThanZero

Output 1 if signal is greater than zero.

```js
const gtz = new Tone.GreaterThanZero();
signal.connect(gtz);
```

## Zero

Outputs a constant zero signal. Useful for creating silent signal paths that won't be optimized away.

```js
const zero = new Tone.Zero();
```

## WaveShaper

Apply a custom transfer function to a signal.

```js
const shaper = new Tone.WaveShaper((x) => {
  // Custom distortion curve
  return Math.tanh(x * 2);
});
signal.connect(shaper);
```

```js
// With a lookup table
const shaper = new Tone.WaveShaper(256, (x) => {
  return x * x * Math.PI;
});
```

| Option | Type | Default | Description |
|---|---|---|---|
| `curve` | number \| function | — | Curve size or function |
| `oversample` | string | `"none"` | `"none"`, `"2x"`, `"4x"` |

## Complex Signal Chains

```js
// Build a custom modulation chain
const lfo = new Tone.LFO("4n", 0, 1).start();

const scale = new Tone.Scale(200, 8000);
const add = new Tone.Add(100);
const pow = new Tone.Pow(0.5);

lfo.chain(scale, add, pow, filter.frequency);
```

```js
// Audio-rate amplitude detection → parameter control
const follower = new Tone.Follower({ attack: 0.005, release: 0.1 });
const scale = new Tone.Scale(0, 20);

synth.connect(follower);
follower.chain(scale, compressor.threshold);
```
