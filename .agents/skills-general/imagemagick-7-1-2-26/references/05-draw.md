# ImageMagick 7.1.2-26 — Drawing and Text

## Table of Contents

- [Draw Primitive](#draw-primitive)
- [Drawing Primitives](#drawing-primitives)
- [Text Annotation](#text-annotation)
- [Fonts](#fonts)
- [Draw Options](#draw-options)

---

## Draw Primitive

The `-draw` option accepts a string of drawing commands. Multiple primitives are separated by spaces.

```bash
magick convert input.jpg \
  -draw "fill red fill-opacity 0.5 circle 200,200 200,100" \
  -draw "stroke blue strokewidth 2 line 50,50 300,300" \
  output.jpg
```

---

## Drawing Primitives

### Basic Shapes

```
circle cx,cy x1,y1           # Circle (center + edge point)
ellipse cx,cy rx,ry start,end # Ellipse (center + radii + arc angles in degrees)
rectangle x1,y1 x2,y2        # Rectangle
roundrectangle x1,y1 x2,y2 rw,rh  # Rounded rectangle
line x1,y1 x2,y2             # Line segment
point x,y                    # Single point
polygon x1,y1 x2,y2 ...      # Polygon (3+ points)
polyline x1,y1 x2,y2 ...     # Open polyline
```

### Text

```
text x,y "string"            # Text at position
```

### Paths

```
path "M x,y L x,y Z"         # SVG-like path commands
```

Path commands: `M` (moveto), `L` (lineto), `H` (horizontal line), `V` (vertical line), `C` (cubic bezier), `S` (smooth cubic), `Q` (quadratic bezier), `T` (smooth quadratic), `A` (ellipse arc), `Z` (close path). Uppercase = absolute, lowercase = relative.

### Image

```
image compose x,y w,h "filename"    # Composite image at position
```

### Color

```
color x,y "color"                  # Draw single pixel
```

### Floodfill

```
fill x,y "color"                   # Floodfill from point
```

### Arc

```
arc x1,y1 x2,y2 start,end          # Arc in bounding box
```

### Matte

```
matte x,y "color"                  # Draw with matte
```

### Push/Pop Graphics State

```
push                       # Save graphics state
  fill red
  circle 100,100 100,50
pop                        # Restore graphics state
```

---

## Text Annotation

### `-annotate`

Annotates image with text. Geometry specifies position.

```bash
# Text at specific position
magick convert input.jpg -annotate +10+10 "Hello World" output.jpg

# Text with font settings
magick convert input.jpg \
  -font DejaVu-Sans -pointsize 36 -fill white -stroke black -strokewidth 1 \
  -gravity Center -annotate 0 "Title" output.jpg

# Multi-line text (use \n)
magick convert input.jpg \
  -annotate +10+10 "Line 1\nLine 2\nLine 3" output.jpg
```

### `-draw text`

More flexible, supports rotation and positioning:

```bash
magick convert input.jpg \
  -draw "font DejaVu-Sans font-size 36 fill white text 10,50 'Hello World'" \
  output.jpg
```

### Text on a Path

```bash
magick convert input.jpg \
  -draw "text 100,100 'path M 0,0 C 100,-50 200,50 300,0'" \
  output.jpg
```

### Text Options

| Option | Description |
|---|---|
| `-font name` | Font family/name |
| `-pointsize value` | Font size in points |
| `-fill color` | Text fill color |
| `-stroke color` | Text outline color |
| `-strokewidth value` | Outline width |
| `-gravity type` | Text placement |
| `-kerning value` | Letter spacing |
| `-interword-spacing value` | Word spacing |
| `-interline-spacing value` | Line spacing |
| `-encoding type` | Text encoding (UTF8, ASCII, etc.) |
| `-direction type` | Text direction (LeftToRight, RightToLeft) |
| `-antialias` | Anti-aliased text |
| `-undercolor color` | Text background color |
| `-style type` | Font style (Normal, Italic, Oblique) |
| `-weight type` | Font weight (Normal, Bold, etc.) |
| `-stretch type` | Font stretch (Condensed, Expanded, etc.) |
| `-family name` | Font family |

---

## Fonts

### Listing Fonts

```bash
magick convert -list font        # List all available fonts
magick convert -list type        # List type definitions
```

### Font Configuration

Fonts are configured in `type.xml` (usually in `/etc/ImageMagick-7/` or `/usr/local/etc/ImageMagick-7/`).

```xml
<font family="DejaVu Sans" style="Normal" weight="400"
      stretch="Normal" format="truetype"
      glyph_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"/>
```

### Common Font Names

- `DejaVu-Sans`, `DejaVu-Serif`, `DejaVu-Sans-Mono`
- `Helvetica`, `Times-Roman`, `Courier`
- `Arial`, `Verdana`, `Georgia` (Windows fonts)
- System fonts via FontConfig

### Complex Scripts

For Arabic, Indic, and other complex scripts, use Pango or RAQM delegates:

```bash
# With Pango coder
magick convert pango:"Hello العربية" output.png

# With RAQM (complex text shaping)
magick convert -define raqm:fontface="DejaVu-Sans" \
  -annotate +10+10 "مرحبا" output.png
```

---

## Draw Options

### Fill and Stroke

```
fill color              # Fill color
fill-opacity value      # Fill opacity (0-1)
stroke color            # Stroke color
stroke-opacity value    # Stroke opacity (0-1)
strokewidth value       # Stroke width
```

### Decoration

```
decorate                # Draw border around text
```

### Clip

```
clip-path "id"          # Use named path as clip mask
clip-units type         # UserSpace, UserSpaceUse, ObjectBoundingBox
```

### Interpolate

```
interpolate method      # Interpolation method for drawing
```

### Example: Complex Drawing

```bash
magick convert xc:none -size 400x300 \
  -draw "
    fill blue circle 200,150 200,50
    fill none stroke white strokewidth 3 circle 200,150 200,80
    fill yellow polygon 200,30 180,70 220,70
    stroke red strokewidth 2 line 50,250 350,250
    font Helvetica font-size 24 fill white text 200,280 'ImageMagick'
  " output.png
```

### Example: Watermark with Rotation

```bash
magick convert input.jpg \
  -draw "
    push
    translate 200,200
    rotate -45
    fill 'rgba(255,255,255,0.3)'
    font Arial font-size 48
    text -200,-10 'WATERMARK'
    pop
  " output.jpg
```
