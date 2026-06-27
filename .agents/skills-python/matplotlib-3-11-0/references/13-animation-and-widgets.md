# Animation and Widgets

## FuncAnimation

The primary way to create animations:

```python
import matplotlib.animation as animation

fig, ax = plt.subplots()
line, = ax.plot([], [], linewidth=2)
ax.set_xlim(0, 10)
ax.set_ylim(-1, 1)

def init():
    line.set_data([], [])
    return line,

def update(frame):
    x = np.linspace(0, 10, 100)
    y = np.sin(x + frame * 0.1)
    line.set_data(x, y)
    return line,

ani = animation.FuncAnimation(
    fig, update, frames=100, init_func=init,
    blit=True, interval=50, repeat=True
)
plt.show()
```

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `fig` | Figure to animate |
| `func` | Update function called per frame |
| `frames` | Number of frames or iterable |
| `init_func` | Initialization function |
| `blit` | Use blitting for performance |
| `interval` | Milliseconds between frames (default 200) |
| `repeat` | Repeat animation (default True) |
| `cache_frame_data` | Cache frame data (default True) |

### Saving animations

```python
# MP4 (requires ffmpeg or Pillow writer)
ani.save('animation.mp4', writer='ffmpeg', fps=30)

# GIF (requires Pillow)
ani.save('animation.gif', writer='pillow', fps=10, dpi=100)

# HTML5 video (for Jupyter)
from matplotlib.animation import html
HTML(ani.to_jshtml())
```

### Available writers

| Writer | Format | Requirements |
|--------|--------|-------------|
| `ffmpeg` | MP4, AVI | ffmpeg installed |
| `pillow` | GIF, PNG sequence | Pillow (built-in) |
| `mencoder` | MP4, AVI | mencoder installed |
| `avconv` | MP4 | avconv installed |

Check available: `animation.writers.available`

### Frame-by-frame with generator

```python
def frame_generator():
    for t in np.linspace(0, 2 * np.pi, 200):
        yield t

ani = animation.FuncAnimation(fig, update, frames=frame_generator)
```

## ArtistAnimation

Pre-render all frames upfront:

```python
fig, ax = plt.subplots()
images = []
for i in range(100):
    data = np.random.randn(10, 10)
    im = ax.imshow(data, cmap='viridis', vmin=-3, vmax=3)
    images.append([im])

ani = animation.ArtistAnimation(fig, images, interval=50, blit=True)
```

## Interactive Widgets

All widgets require a pre-created axes:

```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.subplots_adjust(left=0.1, bottom=0.2)
```

### Slider

```python
from matplotlib.widgets import Slider

ax_slider = fig.add_axes([0.15, 0.05, 0.7, 0.03])
slider = Slider(ax_slider, 'Frequency', 0.1, 10.0, valinit=1.0)

def update(val):
    freq = slider.val
    y = np.sin(2 * np.pi * freq * x)
    line.set_ydata(y)
    fig.canvas.draw_idle()

slider.on_changed(update)
```

### Button

```python
from matplotlib.widgets import Button

ax_button = fig.add_axes([0.81, 0.05, 0.1, 0.04])
button = Button(ax_button, 'Reset', hovercolor='0.975')

def reset(event):
    slider.reset()
    fig.canvas.draw_idle()

button.on_clicked(reset)
```

### Radio Buttons

```python
from matplotlib.widgets import RadioButtons

ax_radio = fig.add_axes([0.02, 0.5, 0.1, 0.15])
choices = ['sin', 'cos', 'tan']
radio = RadioButtons(ax_radio, choices, active=0)

def update(label):
    func = {'sin': np.sin, 'cos': np.cos, 'tan': np.tan}[label]
    line.set_ydata(func(x))
    fig.canvas.draw_idle()

radio.on_clicked(update)
```

### Check Buttons

```python
from matplotlib.widgets import CheckButtons

ax_check = fig.add_axes([0.02, 0.75, 0.1, 0.1])
labels = ['Line A', 'Line B']
check = CheckButtons(ax_check, labels, [True, False])

def update(label):
    if label == 'Line A':
        line1.set_visible(not line1.get_visible())
    else:
        line2.set_visible(not line2.get_visible())
    fig.canvas.draw_idle()

check.on_clicked(update)
```

### Cursor

```python
from matplotlib.widgets import Cursor

cursor = Cursor(ax, useblit=True, color='red', linewidth=1)
# Shows crosshair that follows mouse
```

### Span Selector

```python
from matplotlib.widgets import SpanSelector

def onselect(xmin, xmax):
    print(f'Selected: {xmin:.2f} to {xmax:.2f}')
    ax.set_xlim(xmin, xmax)
    fig.canvas.draw_idle()

span = SpanSelector(ax, onselect, direction='horizontal',
                    useblit=True, rectprops=dict(alpha=0.2, facecolor='blue'))
```

### SelectionBoxes

```python
from matplotlib.widgets import SelectionBoxes

def onclick(event):
    print(f'Box: x={event.xdata:.2f}, y={event.ydata:.2f}')

selector = SelectionBoxes(ax, onclick)
```

## Event-Driven Interactivity

```python
fig, ax = plt.subplots()
line, = ax.plot(x, y)

# Mouse click
def on_click(event):
    if event.inaxes == ax:
        print(f'Clicked: ({event.xdata:.2f}, {event.ydata:.2f})')
        # Add marker at click
        ax.plot(event.xdata, event.ydata, 'ro')
        fig.canvas.draw_idle()

fig.canvas.mpl_connect('button_press_event', on_click)

# Key press
def on_key(event):
    if event.key == 'r':
        line.set_ydata(np.random.randn(len(x)))
        fig.canvas.draw_idle()
    elif event.key == 'q':
        plt.close()

fig.canvas.mpl_connect('key_press_event', on_key)

# Mouse motion
def on_motion(event):
    if event.inaxes == ax:
        status_text.set_text(f'x={event.xdata:.2f}, y={event.ydata:.2f}')
        fig.canvas.draw_idle()

fig.canvas.mpl_connect('motion_notify_event', on_motion)
```

## Layout Tips for Widgets

- Use `subplots_adjust()` to reserve space for widgets
- Place sliders at bottom, buttons/radios on sides
- Keep widget axes narrow (height ~0.03–0.05 of figure)
- Use `fig.canvas.draw_idle()` instead of `fig.canvas.draw()` for responsiveness
