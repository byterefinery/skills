# Models & Languages — RapidOCR 3.9.2

## Model Versions

### PP-OCRv6 (Latest)

Unified multilingual models — single model handles 50+ languages for both detection and recognition.

**Detection models:**
| Model | Size | Languages |
|---|---|---|
| `multi_PP-OCRv6_det_tiny` | ~3MB | 50+ (all except Japanese) |
| `multi_PP-OCRv6_det_small` | ~8MB | 50+ |
| `multi_PP-OCRv6_det_medium` | ~25MB | 50+ |

**Recognition models:**
| Model | Size | Languages |
|---|---|---|
| `multi_PP-OCRv6_rec_tiny` | ~8MB | 50+ (all except Japanese) |
| `multi_PP-OCRv6_rec_small` | ~20MB | 50+ |
| `multi_PP-OCRv6_rec_medium` | ~55MB | 50+ |

### PP-OCRv5

Language-specific models with improved accuracy over v4.

**Detection:**
- `ch_PP-OCRv5_det_mobile` — Chinese + English detection
- `ch_PP-OCRv5_det_server` — Chinese + English detection (larger)

**Recognition (language-specific):**
- `ch_PP-OCRv5_rec_mobile` / `ch_PP-OCRv5_rec_server` — Chinese
- `en_PP-OCRv5_rec_mobile` — English
- `korean_PP-OCRv5_rec_mobile` — Korean
- `latin_PP-OCRv5_rec_mobile` — Latin script languages
- `eslav_PP-OCRv5_rec_mobile` — South Slavic languages
- `th_PP-OCRv5_rec_mobile` — Thai
- `el_PP-OCRv5_rec_mobile` — Greek
- `arabic_PP-OCRv5_rec_mobile` — Arabic
- `cyrillic_PP-OCRv5_rec_mobile` — Cyrillic
- `devanagari_PP-OCRv5_rec_mobile` — Devanagari
- `ta_PP-OCRv5_rec_mobile` — Tamil
- `te_PP-OCRv5_rec_mobile` — Telugu

**Classification:**
- `ch_PP-LCNet_x0_25_textline_ori_cls_mobile` — text orientation (0°/180°)
- `ch_PP-LCNet_x1_0_textline_ori_cls_server` — text orientation (larger)

**Image shape:** `[3, 80, 160]` for classification (different from v4's `[3, 48, 192]`)

### PP-OCRv4

Original model family, most language coverage for non-v6 languages.

**Detection:**
- `ch_PP-OCRv4_det_mobile` — Chinese + English
- `ch_PP-OCRv4_det_server` — Chinese + English (larger)
- `en_PP-OCRv3_det_mobile` — English only
- `multi_PP-OCRv3_det_mobile` — Multilingual

**Recognition (language-specific):**
- `ch_PP-OCRv4_rec_mobile` / `ch_PP-OCRv4_rec_server` — Chinese
- `ch_doc_PP-OCRv4_rec_server` — Chinese document layout
- `en_PP-OCRv4_rec_mobile` — English
- `chinese_cht_PP-OCRv3_rec_mobile` — Traditional Chinese
- `japan_PP-OCRv4_rec_mobile` — Japanese
- `korean_PP-OCRv4_rec_mobile` — Korean
- `arabic_PP-OCRv4_rec_mobile` — Arabic
- `cyrillic_PP-OCRv3_rec_mobile` — Cyrillic
- `devanagari_PP-OCRv4_rec_mobile` — Devanagari
- `latin_PP-OCRv3_rec_mobile` — Latin script
- `ta_PP-OCRv4_rec_mobile` — Tamil
- `te_PP-OCRv4_rec_mobile` — Telugu
- `ka_PP-OCRv4_rec_mobile` — Georgian

**Classification:**
- `ch_ppocr_mobile_v2.0_cls_mobile` — text orientation

## Supported Recognition Languages

### LangRec Enum Values

| Enum | Value | Script |
|---|---|---|
| `LangRec.CH` | `"ch"` | Simplified Chinese |
| `LangRec.CH_DOC` | `"ch_doc"` | Chinese document layout |
| `LangRec.EN` | `"en"` | English |
| `LangRec.ARABIC` | `"arabic"` | Arabic (RTL) |
| `LangRec.CHINESE_CHT` | `"chinese_cht"` | Traditional Chinese |
| `LangRec.CYRILLIC` | `"cyrillic"` | Cyrillic |
| `LangRec.DEVANAGARI` | `"devanagari"` | Devanagari |
| `LangRec.JAPAN` | `"japan"` | Japanese |
| `LangRec.KOREAN` | `"korean"` | Korean |
| `LangRec.KA` | `"ka"` | Georgian |
| `LangRec.LATIN` | `"latin"` | Latin script (multi-lang) |
| `LangRec.TA` | `"ta"` | Tamil |
| `LangRec.TE` | `"te"` | Telugu |
| `LangRec.ESLAV` | `"eslav"` | South Slavic |
| `LangRec.TH` | `"th"` | Thai |
| `LangRec.EL` | `"el"` | Greek |

### PP-OCRv6 Additional Languages

PP-OCRv6 multilingual models support these additional language codes:
`af`, `az`, `bs`, `ca`, `cs`, `cy`, `da`, `de`, `es`, `et`, `eu`, `fi`, `fr`, `ga`, `gl`, `hr`, `hu`, `id`, `is`, `it`, `ku`, `la`, `lb`, `lt`, `lv`, `mi`, `ms`, `mt`, `nl`, `no`, `oc`, `pl`, `pt`, `qu`, `rm`, `ro`, `rs_latin`, `sk`, `sl`, `sq`, `sv`, `sw`, `tl`, `tr`, `uz`, `vi`, `french`, `german`

Plus aliases: `zh` → `ch`, `zh_cn` → `ch`, `zh_tw` → `chinese_cht`, `ja`/`jp` → `japan`, `ko` → `korean`

## Model Sizes

| Size | Typical use case | Approx model size |
|---|---|---|
| `tiny` | Edge devices, fastest | 3-8MB |
| `mobile` | Mobile, embedded, default | 8-20MB |
| `small` | Balanced speed/accuracy | 8-25MB |
| `medium` | Best accuracy | 25-55MB |
| `server` | Maximum accuracy (v4/v5) | 20-80MB |

## Model Resolution

Models auto-download from ModelScope on first use. Each model has a SHA256 hash for integrity verification.

### Model Naming Convention

```
{lang}_{version}_{task}_{size}.{ext}

Examples:
  ch_PP-OCRv4_det_mobile.onnx      — Chinese, v4, detection, mobile
  multi_PP-OCRv6_rec_small.onnx    — Multilingual, v6, recognition, small
  ch_ppocr_mobile_v2.0_cls_mobile.onnx — Chinese, v2.0, classification, mobile
```

### Character Dictionaries

- **ONNX Runtime:** Character dict is embedded in the ONNX model metadata — no separate file needed
- **Other engines:** Character dict downloaded as separate `.txt` file (e.g., `ppocr_keys_v1.txt`)

### Custom Models

To use custom/fine-tuned models:

```python
engine = RapidOCR(params={
    "Det.model_path": "/path/to/my_det.onnx",
    "Rec.model_path": "/path/to/my_rec.onnx",
    "Rec.rec_keys_path": "/path/to/my_dict.txt",
})
```

Or via config YAML:

```yaml
Det:
  model_path: /path/to/my_det.onnx

Rec:
  model_path: /path/to/my_rec.onnx
  rec_keys_path: /path/to/my_dict.txt
```

When `model_path` is set, model download is skipped and the specified file is used directly.
