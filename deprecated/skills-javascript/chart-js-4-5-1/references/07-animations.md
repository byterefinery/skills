# Animations Reference

## Animation Configuration

Namespace: `options.animations`

| Property | Type | Default | Description |
|---|---|---|---|
| `duration` | `number` | `1000` | Animation duration in ms |
| `easing` | `string` | `'easeOutQuart'` | Easing function |
| `delay` | `number` \| `function` | | Delay before animation starts |
| `loop` | `boolean` | `false` | Loop animation |

### Easing Functions

Available easings: `linear`, `easeInQuad`, `easeOutQuad`, `easeInOutQuad`, `easeInCubic`, `easeOutCubic`, `easeInOutCubic`, `easeInQuart`, `easeOutQuart`, `easeInOutQuart`, `easeInQuint`, `easeOutQuint`, `easeInOutQuint`, `easeInSine`, `easeOutSine`, `easeInOutSine`, `easeInExpo`, `easeOutExpo`, `easeInOutExpo`, `easeInCirc`, `easeOutCirc`, `easeInOutCirc`, `easeInElastic`, `easeOutElastic`, `easeInOutElastic`, `easeInBack`, `easeOutBack`, `easeInOutBack`, `easeInBounce`, `easeOutBounce`, `easeInOutBounce`.

## Property Animations

Animate specific properties:

```javascript
options: {
  animations: {
    numbers: {
      duration: 2000,
      easing: 'easeOutBounce'
    },
    colors: {
      duration: 500
    },
    progression: {
      easing: 'linear'
    }
  }
}
```

### Tension Animation

Animate line smoothness:

```javascript
options: {
  animations: {
    tension: {
      duration: 1000,
      easing: 'linear',
      from: 1,
      to: 0,
      loop: true
    }
  }
}
```

## Transitions

Define animations for specific state changes:

```javascript
options: {
  transitions: {
    active: {
      animation: {
        duration: 0
      }
    },
    resize: {
      animation: {
        duration: 0
      }
    },
    show: {
      animations: {
        x: { from: 0 },
        y: { from: 0 }
      }
    },
    hide: {
      animations: {
        x: { to: 0 },
        y: { to: 0 }
      }
    }
  }
}
```

### Transition Modes

| Mode | When |
|---|---|
| `active` | When elements become active (hover) |
| `resize` | When chart is resized |
| `show` | When dataset is shown |
| `hide` | When dataset is hidden |
| `default` | Default update animation |
| `none` | No animation |

## Disable Animations

```javascript
options: {
  animation: false
}
```

Or for specific updates:

```javascript
chart.update('none');
```

## Custom Animation Callbacks

```javascript
options: {
  animation: {
    onProgress: (animation) => {
      // Called during animation
      console.log('Progress:', animation.currentProgress);
    },
    onComplete: (animation) => {
      // Called when animation completes
      console.log('Animation complete');
    }
  }
}
```

## Per-Dataset Animation Delay

```javascript
options: {
  animation: {
    delay(context) {
      return context.dataIndex * 100;  // stagger by data index
    }
  }
}
```
