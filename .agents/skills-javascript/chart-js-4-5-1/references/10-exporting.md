# Exporting Reference

## toBase64Image

Export chart as a base64-encoded data URL:

```javascript
const dataURL = chart.toBase64Image('image/png');
// or
const dataURL = chart.toBase64Image('image/jpeg', 0.8);  // quality 0-1
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `type` | `string` | `'image/png'` | MIME type: `image/png`, `image/jpeg`, `image/webp` |
| `quality` | `number` | `1` | JPEG/WebP quality (0-1) |

### Usage Examples

```javascript
// Download as PNG
const link = document.createElement('a');
link.download = 'chart.png';
link.href = chart.toBase64Image();
link.click();

// Download as JPEG
const link = document.createElement('a');
link.download = 'chart.jpg';
link.href = chart.toBase64Image('image/jpeg', 0.9);
link.click();

// Embed in HTML
const img = document.createElement('img');
img.src = chart.toBase64Image();
document.body.appendChild(img);
```

## Canvas Export

Access the raw canvas element:

```javascript
const canvas = chart.canvas;

// Get image data
const imageData = canvas.toDataURL('image/png');

// Get blob
canvas.toBlob((blob) => {
  const url = URL.createObjectURL(blob);
  // use url
});

// Get raw pixels
const ctx = canvas.getContext('2d');
const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
```

## High-Quality Export

For higher resolution exports, create a temporary canvas:

```javascript
function exportHighQuality(chart, scale = 2) {
  const originalCanvas = chart.canvas;
  const originalWidth = originalCanvas.width;
  const originalHeight = originalCanvas.height;

  // Create high-res canvas
  const hiResCanvas = document.createElement('canvas');
  hiResCanvas.width = originalWidth * scale;
  hiResCanvas.height = originalHeight * scale;
  const hiResCtx = hiResCanvas.getContext('2d');
  hiResCtx.scale(scale, scale);

  // Draw original canvas
  hiResCtx.drawImage(originalCanvas, 0, 0);

  return hiResCanvas.toDataURL('image/png');
}
```

## Printing

### Print Chart

```javascript
function printChart(chart) {
  const printWindow = window.open('', '_blank');
  printWindow.document.write(`
    <html>
      <head><title>Chart</title></head>
      <body>
        <img src="${chart.toBase64Image()}" style="max-width: 100%">
        <script>window.print();<\/script>
      </body>
    </html>
  `);
}
```

### Print with Page Layout

```javascript
window.addEventListener('beforeprint', () => {
  // Resize all charts for print
  for (const id in Chart.instances) {
    Chart.instances[id].resize(1200, 600);
  }
});

window.addEventListener('afterprint', () => {
  // Restore original size
  for (const id in Chart.instances) {
    Chart.instances[id].resize();
  }
});
```

## Server-Side Export

For server-side rendering, use a Node.js canvas implementation:

```bash
npm install canvas chart.js
```

```javascript
import { createCanvas } from 'canvas';
import { Chart } from 'chart.js';

const canvas = createCanvas(800, 400);
const chart = new Chart(canvas, {
  type: 'bar',
  data: {
    labels: ['A', 'B', 'C'],
    datasets: [{ data: [10, 20, 30] }]
  }
});

// Wait for render to complete
chart.render().then(() => {
  const buffer = canvas.toBuffer('image/png');
  // save buffer or send as response
  chart.destroy();
});
```

## SVG Export

Chart.js renders to canvas, not SVG. For SVG output, consider:

1. **chartjs-to-image** — convert canvas to SVG path data
2. **Re-render with a library that supports SVG** — like D3.js or Apache ECharts
3. **Use a plugin** — community plugins exist for SVG export

## PDF Export

```javascript
// Using jsPDF
import jsPDF from 'jspdf';

function exportToPDF(chart, filename = 'chart.pdf') {
  const pdf = new jsPDF();
  const imgData = chart.toBase64Image();
  const imgWidth = 190;  // A4 width minus margins
  const imgHeight = (chart.canvas.height / chart.canvas.width) * imgWidth;
  pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);
  pdf.save(filename);
}
```
