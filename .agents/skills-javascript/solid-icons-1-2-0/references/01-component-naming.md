# Component name derivation

How the build converts an icon's SVG file path into the exported component name. Source: `packages/solid-icons/src/build/utils/file-name.ts`, `utils/normalize-name.ts`, and `constants.ts`.

## Formula

```
<CapitalizedAbbrev>[<Style>]<PascalCaseFileName>
```

1. `<CapitalizedAbbrev>` — the pack's `shortName` with its first letter capitalized (`tb` → `Tb`, `fa` → `Fa`).
2. `<Style>` — optional. Applied only when the SVG sits in a subfolder below the pack's root path: the folder name gets its first letter capitalized and is appended. Non-alphanumeric characters in the folder name are stripped. Two capitalized folder names are remapped by `tinyStyles`: `Filled` → `Fill`, `Outlined` → `Outline`. All other folder names pass through as-is (e.g. `Solid` → `Solid`).
3. `<PascalCaseFileName>` — the file name without extension, each dash-separated segment with its first letter uppercased and the dashes removed. All other characters keep their original casing.

## Documented examples

- `tb` pack, `brand-solidjs.svg` → `Tb` + `Brand` + `Solidjs` = `TbBrandSolidjs` (README usage example).
- `fa` pack, `solid/anchor-circle-check.svg` → `Fa` + `Solid` (subfolder style) + `AnchorCircleCheck` = `FaSolidAnchorCircleCheck` (test-app import).

Note the second segment of `BrandSolidjs` — `solidjs` keeps its lowercase `j` because only the first letter of each dash-separated segment is uppercased.

## Per-pack file name normalization

Some packs normalize the raw file name before naming (from `normalize-name.ts`):

| Pack | Normalization |
| ---- | ------------- |
| `wi` (Weather Icons) | Drops the first 2 characters of the file name |
| `im` (IcoMoon Free)   | Drops the first 3 characters of the file name |
| `bi` (BoxIcons)       | Drops the first 3 characters of the file name |
| `oc` (Octicons)       | Removes `12` anywhere, replaces `16` with `2` and `24` with `3`, then strips all dashes |

All other packs use the file name as-is.

## Style folder mapping

`tinyStyles` in `constants.ts` — applied to the capitalized subfolder name before it is appended:

| Folder name (capitalized) | Appended style |
| ------------------------- | -------------- |
| `Filled`                  | `Fill`         |
| `Outlined`                | `Outline`      |
| anything else             | unchanged (e.g. `Solid`) |
