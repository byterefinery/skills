# Files handling

## Uploading

To upload files, add a `file` field to the collection, then create/update a record with a `multipart/form-data` request (Records create/update APIs). Each file is stored with the original (sanitized) filename plus a random suffix — e.g. `test_52iwbgds7l.png`. Default max file size per field is **~5MB** (adjustable in field options; large files degrade performance).

```js
const pb = new PocketBase('http://127.0.0.1:8090');

// JSON body + File/Blob instances (SDK converts to FormData automatically)
const created = await pb.collection('example').create({
    title: 'Hello world!',
    documents: [file1, file2], // File/Blob instances; array if Max Files > 1
});

// or plain FormData
const formData = new FormData();
formData.append('title', 'Hello world!');
fileInput.addEventListener('change', function () {
    for (const file of this.files) {
        formData.append('documents', file, file.name);
    }
});
await pb.collection('example').create(formData);
```

For multiple-file fields use the name modifiers to merge with existing files:

```js
await pb.collection('example').update('RECORD_ID', { 'documents+': [file3] }); // append
await pb.collection('example').update('RECORD_ID', { '+documents': file4 });   // prepend
```

React Native (Android/iOS) has a non-standard `FormData` — file entries need the explicit object syntax `formData.append('documents', { uri, name, type })`.

## Deleting

Set the file field to a zero value (empty string / `[]`) to delete all its files. For a multiple-file field, delete individual files by suffixing the field name with `-` and listing the filenames:

```js
await pb.collection('example').update('RECORD_ID', { documents: '' });            // delete all
await pb.collection('example').update('RECORD_ID', { 'documents-': ['a.png', 'b.png'] }); // individual
```

## File URLs

Every file is accessible at:

```
http://127.0.0.1:8090/api/files/COLLECTION_ID_OR_NAME/RECORD_ID/FILENAME
```

- `?download` — force download (attachment)
- `?thumb=FORMAT` — generated image thumbnail (jpg/png/gif-first-frame, partially webp). If the size is invalid or the file is not an image, the original file is returned.

Thumb formats:

| Format | Meaning |
|---|---|
| `WxH` (e.g. `100x300`) | crop to WxH viewbox from center |
| `WxHt` | crop from top |
| `WxHb` | crop from bottom |
| `WxHf` | fit inside WxH without cropping |
| `0xH` (e.g. `0x300`) | resize to H height preserving aspect |
| `Wx0` (e.g. `100x0`) | resize to W width preserving aspect |

SDK helper: `pb.files.getURL(record, filename, { thumb: '100x300' })`.

## Protected files

An auth collection can mark its file fields as **protected** — then anonymous requests get 403. Clients request a short-lived file token via `POST /api/files/token` (or `pb.files.getToken()`) and pass it as `?token=...` on the file URL. The file download context is `"protectedFile"` in API rules.

## Storage backends

Files are stored on local disk (`pb_data/storage/`) or S3-compatible storage, configured per filesystem (`storage` for record files, `avatars` for OAuth avatars) in Dashboard → Settings. Test the S3 connection with `POST /api/settings/test/s3` or the SDK `pb.settings.testS3()`.
