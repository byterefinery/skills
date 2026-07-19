# 09 — Files & Storage

## Overview

PocketBase provides a thin abstraction between local filesystem and S3-compatible storage. Configured via Dashboard → Settings → Files storage. Default max file size: ~5MB per field (adjustable).

## Uploading Files

### Via SDK (JavaScript)

```javascript
// Create record with files
const record = await pb.collection('articles').create({
    title: 'Hello world!',
    documents: [
        new File(['content 1...'], 'file1.txt'),
        new File(['content 2...'], 'file2.txt'),
    ]
})

// FormData approach
const formData = new FormData()
formData.append('title', 'Hello world!')
formData.append('documents', fileInput.files[0])

const record = await pb.collection('articles').create(formData)
```

### Via SDK (Dart)

```dart
import 'package:http/http.dart' as http;

final record = await pb.collection('articles').create(
    body: {'title': 'Hello world!'},
    files: [
        http.MultipartFile.fromString('documents', 'content...', filename: 'file1.txt'),
        http.MultipartFile.fromString('documents', 'content...', filename: 'file2.txt'),
    ],
);
```

### Appending Files

```javascript
// Append to existing files
await pb.collection('articles').update('RECORD_ID', {
    'documents+': new File(['content'], 'file3.txt'),
})

// Prepend
await pb.collection('articles').update('RECORD_ID', {
    '+documents': new File(['content'], 'file0.txt'),
})
```

## Deleting Files

```javascript
// Delete all files in a field
await pb.collection('articles').update('RECORD_ID', { documents: [] })

// Delete individual files
await pb.collection('articles').update('RECORD_ID', {
    'documents-': ['file1.pdf', 'file2.txt'],
})
```

## File URLs

```
http://127.0.0.1:8090/api/files/{collection}/{record}/{filename}
```

### Thumb (image resizing)

```
http://127.0.0.1:8090/api/files/articles/abc123/photo.png?thumb=100x300
```

Supported: jpg, png, gif (first frame), partially webp (stored as png).

### Force download

```
http://127.0.0.1:8090/api/files/articles/abc123/file.pdf?download=1
```

### SDK helper

```javascript
const record = await pb.collection('articles').getOne('RECORD_ID')
const url = pb.files.getURL(record, record.documents[0], { thumb: '100x250' })
```

## Protected Files

For sensitive files (IDs, contracts), enable protected file tokens:

```javascript
// Request a protected file token
const token = await pb.collection('articles').requestFileToken('RECORD_ID', 'secret.pdf', 60)

// Access with token
const url = pb.files.getURL(record, 'secret.pdf', { token })
```

The file token has configurable duration (default 5 minutes). The `fileToken` duration is set per auth collection.

## Storage Configuration

### Local (default)

Files stored in `pb_data/files/{collectionId}/{recordId}/{filename}`.

### S3

Configure in Dashboard → Settings → Files storage:
- Bucket name
- Provider (AWS, GCS, custom S3-compatible)
- Region
- Base URL
- Access key ID
- Secret access key
- Force path style (for minio, etc.)

## Filesystem API (Go)

```go
fsys, err := app.NewFilesystem()
if err != nil { return err }
defer fsys.Close()

// Read file
r, err := fsys.GetReader("collectionId/recordId/filename.ext")
if err != nil { return err }
defer r.Close()

content := new(bytes.Buffer)
io.Copy(content, r)

// Upload
err = fsys.Upload([]byte("content"), "key/path/file.txt")
err = fsys.UploadFile(file, "key/path/file.txt")
err = fsys.UploadMultipart(multipartHeader, "key/path/file.txt")

// Delete
err = fsys.Delete("key/path/file.txt")

// List
files, err := fsys.List("prefix/")
```

## Filesystem API (JS)

```javascript
let fsys = $app.newFilesystem()
try {
    let reader = fsys.getReader("collectionId/recordId/filename.ext")
    // use reader...
    reader.close()
} finally {
    fsys.close()
}

fsys.upload(new TextEncoder().encode("content"), "key/file.txt")
fsys.delete("key/file.txt")
let files = fsys.list("prefix/")
```

## File Field Options

```go
&core.FileField{
    Name:        "avatar",
    Required:    false,
    MaxSelect:   1,              // 1 = single, 2+ = multiple
    MaxFileSize: 2 * 1024 * 1024, // 2MB
    MimeTypes:   []string{"image/jpeg", "image/png", "image/webp"},
    Thumbs:      []string{"100x100", "300x300"},
}
```

```javascript
{
    name:        "avatar",
    type:        "file",
    required:    false,
    maxSelect:   1,
    maxFileSize: 2 * 1024 * 1024,
    mimeTypes:   ["image/jpeg", "image/png"],
    thumbs:      ["100x100", "300x300"],
}
```

## File Operations in Records (Go)

```go
// Set file
f, _ := filesystem.NewFileFromPath("/local/path/file.txt")
record.Set("documents", f)

// Multiple files
record.Set("documents", []*filesystem.File{f1, f2})

// From URL
f, _ := filesystem.NewFileFromURL(context.Background(), "https://example.com/file.pdf")
record.Set("documents", f)

// From bytes
f, _ := filesystem.NewFileFromBytes([]byte("content"), "file.txt")
record.Set("documents", f)

// Delete individual files
record.Set("documents-", "file1.txt")
record.Set("documents-", []string{"file1.txt", "file2.txt"})

// Reset (delete all)
record.Set("documents", nil)

// Save
app.Save(record)
```

## Notes

- Files are stored with sanitized original filename + random suffix (e.g., `photo_52iwbgds7l.png`)
- DB stores only the filename, not the file content
- Old files are auto-deleted when record is updated with new files
- `Close()` must be called on filesystem instances and file readers
- For large files, use S3 storage to avoid degrading app performance
- File field size limits apply per file, not total
