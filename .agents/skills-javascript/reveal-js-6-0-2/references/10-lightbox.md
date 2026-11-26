# Lightbox previews

Overlay previews for images, video, and links (source: `demo.html`, `js/controllers/overlay.js`, `js/config.ts`).

| Attribute | Applies to | Behavior |
|---|---|---|
| `data-preview-image` | image elements / links | Opens an image overlay. With a value, the value is the image URL; on an `<img>` you can rely on its own src (`<img src="image.png" data-preview-image="image.png">` and bare `data-preview-image` both appear in the demo) |
| `data-preview-video` | image or video elements / links | Opens a video overlay; commonly a thumbnail `<img>` with `data-preview-video="video.mp4"` pointing at the video |
| `data-preview-link` | any element, including non-anchors | Opens the element's href/URL in an iframe overlay. `data-preview-link="false"` opts out |
| `previewLinks` (config) | all `a[href]` | When `true` (default `false`), plain links open in the iframe preview overlay; `data-preview-link="false"` on a link opts it out |

Closing the overlay: `ESC` or `C` (the core closes overlays on these keys before handling overview toggling).

The internal state tracks the previewed URL and a fit mode (`none`, `scale-down`, `contain`, `cover` via `getState().previewFit`).
