# Tree View

`@mui/x-tree-view` (Community) and `@mui/x-tree-view-pro` (drag-and-drop). Two component variants: `SimpleTreeView` (static JSX children) and `RichTreeView` (dynamic `items` array).

- [Simple Tree View](#simple-tree-view)
- [Rich Tree View](#rich-tree-view)
- [Tree Item customization (v8)](#tree-item-customization-v8)
- [Selection and expansion](#selection-and-expansion)
- [Lazy loading and headless](#lazy-loading-and-headless)
- [Drag and drop (Pro)](#drag-and-drop-pro)
- [Accessibility](#accessibility)

## Simple Tree View

Items as JSX — best for hardcoded, small trees:

```tsx
import { SimpleTreeView } from '@mui/x-tree-view/SimpleTreeView';
import { TreeItem } from '@mui/x-tree-view/TreeItem';

<SimpleTreeView aria-label="Packages" defaultExpandedItems={['dg']}>
  <TreeItem label="@mui/x-data-grid" itemId="dg" icon={<DataGridIcon />}>
    <TreeItem label="Community" itemId="dg-c" />
    <TreeItem label="Pro" itemId="dg-p" />
  </TreeItem>
</SimpleTreeView>;
```

- `itemId` is required on each `TreeItem` (unique within the tree).
- `label`, `icon`, `iconContainer`, `content`, `actions` — visual parts (see customization below).
- Events: `onItemSelection`, `onItemExpansion`, `onItemClick` (content clicks — v8: item-level `onClick`/`onMouseDown` now target the item root, so use the tree's `onItemClick` for content clicks).

## Rich Tree View

Items from data — best for dynamic, large, or editable trees:

```tsx
import { RichTreeView } from '@mui/x-tree-view/RichTreeView';

const items = [
  { id: 'grid', label: 'Data Grid', children: [{ id: 'grid-c', label: 'Community' }] },
  { id: 'pickers', label: 'Pickers', children: [...] },
];

<RichTreeView
  items={items}
  getItemChildren={(item) => item.children ?? item.nodes} // custom children key
  defaultExpandedItems={['grid']}
  defaultSelectedItems={['grid-c']}
  multiSelect
  onSelectedItemsChange={(ids) => ...}
  onItemsExpansionChange={(ids) => ...}
/>;
```

- Item shape: `{ id, label, children?, isExpandable? }` — any object works; `getItemChildren` maps the children key, `getItemLabel` maps the label.
- Root children come from `items` directly; nested via `children` (or `getItemChildren`).
- `isExpandable` on a leaf to show/hide the expand arrow.

## Tree Item customization (v8)

v8 replaced `ContentComponent`/`ContentProps` (removed) with **slots**, **slotProps**, and the **`useTreeItem`** hook:

```tsx
<TreeItem
  label="Custom"
  itemId="c"
  slots={{
    label: MyLabel,        // or 'content' for the whole content area
    icon: MyIcon,
    iconContainer: MyIconContainer,
    actions: MyActions,    // right-side actions area
  }}
  slotProps={{ label: { className: 'my-label' } }}
/>;
```

- Parts: `label` (text), `content` (label+icon wrapper), `icon`, `iconContainer` (chevron container), `actions`.
- `useTreeItem` inside a custom item gives `selected`, `expanded`, `publicAPI` (`selectItem()`, `setItemsExpansion()`), `getItemProps` for the root element.
- `TreeItem2` and its utils were renamed to `TreeItem` + `TreeItemContext`/`TreeItemProps`-style names in v8 (the `2` suffix is gone).

## Selection and expansion

- `defaultSelectedItems` / `selectedItems` (controlled), `onSelectedItemsChange(ids)`, `multiSelect`.
- `defaultExpandedItems` / `expandedItems`, `onItemsExpansionChange(ids)`.
- v8: Rich Tree View supports **automatic parents and children selection** — selecting a parent can auto-select descendants (and vice versa) via propagation props.
- Public API: `apiRef.current.selectItem(id)`, `setItemsExpansion(ids, expanded?)`, `getRootChildren()`, `getItemChildren(id)`; v8: don't call public API methods inside render (moved to effects).
- `onItemClick(params)` on the tree for content clicks; `onItemSelection` for checkbox/label selection.

## Lazy loading and headless

- Lazy children: `getItemChildren` can return children on demand; combined with `loading` state on items for async trees.
- Headless usage: `useTreeViewApiRef`, `useTreeItem` (item-level context: `selected`, `expanded`, `focused`, `publicAPI`, `getItemProps`), and the virtualization hook for rendering only visible items in very large trees.

## Drag and drop (Pro)

`RichTreeViewPro` from `@mui/x-tree-view-pro`:

```tsx
import { RichTreeViewPro } from '@mui/x-tree-view-pro/RichTreeViewPro';
import { TreeItemDragAndDropOverlay } from '@mui/x-tree-view-pro/TreeItemDragAndDropOverlay';

<RichTreeViewPro
  items={items}
  itemsReordering
  canMoveItemToNewPosition={({ item, target, position }) => position !== 'inside'} // drop policy
  onItemPositionChange={({ itemId, oldPosition, newPosition }) => persist(itemId, newPosition)}
  slots={{ dragAndDropOverlay: TreeItemDragAndDropOverlay }}
/>;
```

- `itemsReordering` enables drag handles on items.
- `onItemPositionChange` gives `{ itemId, oldPosition: { parentId, index }, newPosition: { parentId, index } }`.
- `canMoveItemToNewPosition` restricts drop targets/positions; `canItemBeDragged`-style checks via the reordering plugin.
- `TreeItemDragAndDropOverlay` renders the item ghost while dragging.
- Dragging from a dedicated handle: use the `dragAndDropHandle` slot.

## Accessibility

- Follows the WAI-ARIA treeview pattern; provide a descriptive `aria-label` or `aria-labelledby` on the tree (otherwise screen readers announce a generic "tree").
- Keyboard: arrows to navigate, Enter/Space to select, Right/Left to expand/collapse (standard ARIA tree behavior).
- `RichTreeView` items need stable ids for correct focus management.
