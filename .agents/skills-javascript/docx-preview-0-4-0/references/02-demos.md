# docx-preview Demos

Working code from the `demo/` directory of the docxjs repo (v0.4.0), for use alongside `renderAsync`.

## TIFF/WMF image preprocessing

`demo/docx-preprocessor.js` — the demo's `preprocessDocx` function. The library does not render TIFF or WMF images, so the demo converts them inside the DOCX zip before rendering: TIFF → PNG (`tiff.js`), WMF → SVG (`WMFJS`), and rewrites `[Content_Types].xml` content types.

Requires globals `JSZip`, `Tiff` (tiff.js), and `WMFJS` (rtf.js WMFJS bundle) to be loaded before the demo's `index.html` loads the library.

```js
async function preprocessDocx(blob) {
    let zip = await JSZip.loadAsync(blob);
    const files = zip.file(/[.](tiff|wmf)?$/);

    if (files.length == 0)
        return blob;

    for (let f of files) {
        const buffer = await f.async("uint8array");

        if (f.name.endsWith(".tiff")) {
            const tiff = new Tiff({ buffer });
            const blob = await new Promise(res => tiff.toCanvas().toBlob(blob => res(blob), "image/png"));
            zip.file(f.name, blob);
        }
        else if (f.name.endsWith(".wmf")) {
            var renderer = new WMFJS.Renderer(buffer);
            var width = 1000;
            var height = 800;
            var res = renderer.render({
                width: width + "px",
                height: height + "px",
                xExt: width,
                yExt: height,
                mapMode: 8 // preserve aspect ratio checkbox
            });
            var svg = res.firstChild;
            svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
            svg.removeAttribute("width");
            svg.removeAttribute("height");
            zip.file(f.name, svg.outerHTML);
        }
    }

    const contentType = await zip.file("[Content_Types].xml");

    if (contentType) {
        const text = await contentType.async("text");
        zip.file("[Content_Types].xml", text.replace(/image\/x-wmf/g, "image/svg+xml"));
    }

    return await zip.generateAsync({ type: "blob" });
}
```

Usage pattern from the demo `index.html`:

```js
// optional, find and convert all tiff/wmf images
let docxBlob = await preprocessDocx(currentDocument);
// render document
let res = await docx.renderAsync(docxBlob, container, null, docxOptions);
```

## Thumbnails (example only)

`demo/thumbnail.example.js` — builds clickable page thumbnails from the rendered page wrappers. This is **not** part of the library; it relies on the default `docx` class prefix (`.docx-wrapper > section`) and the `breakPages` option producing one `section` per page.

```js
function renderThumbnails(docxContainer, thumbnailsContainer) {
    const sections = docxContainer.querySelectorAll('.docx-wrapper>section');

    thumbnailsContainer.innerHTML = "";

    for (let i = 0; i < sections.length; i++) {
        const id = `docx-page-${i + 1}`;
        const thumbnail = document.createElement('a');

        thumbnail.className = 'docx-thumbnail-item';
        thumbnail.href = `#${id}`;
        thumbnail.innerText = `${i + 1}`;
        thumbnailsContainer.appendChild(thumbnail);

        sections[i].setAttribute("id", id);
    }
}
```

Call it **after** `renderAsync` resolves, passing the body container and a container for the thumbnails. The demo pairs it with `demo/thumbnail.example.css` for the thumbnail styling.

## Demo app options menu

The demo `index.html` toggles every boolean option live via a dropdown, using:

```js
const docxOptions = Object.assign({}, docx.defaultOptions, {
    debug: true,
    experimental: true,
    hideWrapperOnPrint: true,
});

Object.keys(docxOptions).filter(key => !/^(className|h)$/i.test(key)).forEach(function(key) {
    // ... checkbox per key, re-render on change:
    //   docxOptions[key] = checkInput.checked;
    //   renderDocx(currentDocument);
});
```
