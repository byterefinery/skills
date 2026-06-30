# Infographic Syntax Reference

The infographic syntax is a concise, YAML-like text format. It is parsed by `parseSyntax()` and converted to `InfographicOptions`. The parser is fault-tolerant — partial or streaming input renders progressively.

## Grammar Overview

```
<document> ::= (<header> | <section>)*
<header>   ::= "infographic" <template-name> ["<"key> <value>"]*
             | "template" <template-name>
             | <template-name>          # implicit, emits warning
<section>  ::= <section-name> ":"? <value>
             | <section-name> ":"?
             | "- " <value>             # list item (under array sections)
             | <key> ":" <value>        # key-value under object sections
             | <key> "." <key> <value>  # dotted path (shorthand)
```

- **Indentation** defines nesting. Spaces and tabs both work (tab = 2 spaces).
- **Comments**: lines starting with `#` or `//` are ignored.
- **Code fences**: lines matching `` ``` `` toggle code fence blocks (ignored by parser).
- **Key-value** uses `:` or `=` as separator, or whitespace (space-separated key value).
- **Dotted keys** create nested objects: `themeConfig.base.text.fill: red` → `{ themeConfig: { base: { text: { fill: 'red' } } } }`.

## Top-Level Sections

| Key | Type | Description |
|---|---|---|
| `infographic` | template name + optional inline options | Shorthand: `infographic <template> <key> <value> ...` |
| `template` | string | Template name (e.g., `list-row-simple-horizontal-arrow`) |
| `design` | object | Custom structure, item, title overrides |
| `data` | object | The content data |
| `theme` | string \| object | Theme name or inline theme config |

> Container-specific options (`width`, `height`, `padding`, `editable`) go in `new Infographic({...})`, not in the syntax.

### Header Shorthands

```
# Full form
infographic list-row-simple-horizontal-arrow

# Using template key
template list-row-simple-horizontal-arrow

# Bare first line (implicit — works but warns)
list-row-simple-horizontal-arrow
```

### Dotted Path Syntax {#dotted-path}

Deep nesting can be flattened with dotted keys:

```
# These are equivalent:
theme.base.text.fill #fff
```

```
theme
  base
    text
      fill #fff
```

Mix dotted keys with indented blocks:

```
theme
  base
    shape
      stroke #654321
  base.text.fill #123456
```

**Rules:**
- Dotted paths work only for **object** fields (e.g., `theme.base.text.fill`).
- Traversing an **array** node (e.g., `data.items.0.label`) produces a syntax error.
- When the same path is assigned multiple times, the **last assignment wins**.

## Data Section

The `data` section holds the content. Keys available:

| Key | Schema | Description |
|---|---|---|
| `title` | string | Infographic title |
| `desc` | string | Infographic description |
| `items` | array | Generic items (works with all templates) |
| `lists` | array | List-type items (for list templates) |
| `sequences` | array | Sequence items (for sequence templates) |
| `root` | object | Single root node with `children` (for hierarchy templates) |
| `compares` | array | Comparison groups (for compare templates) |
| `nodes` | array | Graph nodes (for relation templates) |
| `relations` | array | Graph edges (for relation templates) |
| `values` | array | Statistics items (for chart templates) |
| `order` | `asc` \| `desc` | Sort order for value-based layouts |
| `illus` | object | Illustration resource overrides |
| `attributes` | object | Custom attribute overrides |

### Item Datum Schema

Each item in `items`, `lists`, `sequences`, `compares`, `values` supports:

| Key | Type | Description |
|---|---|---|
| `id` | string | Unique identifier (auto-assigned from `label` if omitted) |
| `label` | string | Display text |
| `desc` | string | Description text |
| `value` | number \| string | Numeric value (for charts, progress) |
| `icon` | string \| object | Icon resource (name, URL, or `{ source, data }` config) |
| `illus` | string \| object | Illustration resource |
| `attributes` | object | Custom SVG attributes applied to the item |
| `group` | string | Group/category (for relation nodes) |
| `category` | string | Category (for statistics) |
| `children` | array | Child items (for hierarchy nodes) |

### Data Types by Template Category

| Template Category | Data Key | Example Templates |
|---|---|---|
| **List** | `lists` or `items` | `list-grid-compact-card`, `list-row-simple-horizontal-arrow` |
| **Sequence** | `sequences` or `items` | `sequence-steps-simple`, `sequence-timeline-done-list` |
| **Hierarchy** | `root` (tree) or `items` (array) | `hierarchy-tree-simple`, `hierarchy-mindmap-compact-card` |
| **Compare** | `compares` or `items` | `compare-swot`, `compare-binary-horizontal-simple-vs` |
| **Relation** | `nodes` + `relations` | `relation-dagre-flow-tb-simple-circle-node` |
| **Statistics** | `values` or `items` | `chart-column-simple`, `chart-pie-plain-text` |

---

## Complete Examples by Type

### 1. List Infographics

List data represents a group of peer items without ordering. Common for checklists, feature lists, rankings.

**Data key:** `lists` (or `items`)

```
infographic list-grid-compact-card
data
  title Enterprise Strengths
  desc Core advantages across different dimensions
  lists
    - label Brand Influence
      desc Strong recognition and trust in target audience
      value 85
      icon mingcute/diamond-2-fill
    - label Technology R&D
      desc Self-developed core systems with continuous innovation
      value 90
      icon mingcute/code-fill
    - label Market Growth
      desc Rapid user scale growth in the past year
      value 78
      icon mingcute/wallet-4-line
    - label Service Satisfaction
      desc High overall score from users on service system
      value 88
      icon mingcute/happy-line
    - label Data Assets
      desc Complete user tagging and profiling system built
      value 92
      icon mingcute/user-4-line
    - label Innovation Capability
      desc New product launch frequency above industry average
      value 83
      icon mingcute/rocket-line
theme
  palette antv
```

**Timeline-style list** (uses `time` field):

```
infographic list-column-vertical-icon-arrow
data
  title Enterprise Development Timeline
  desc Key strategic actions and milestones by year
  lists
    - label 2018
      desc Company founded, initial team building and product positioning
      time 2018
      icon mingcute/calendar-fill
    - label 2020
      desc Released first core product, opened regional market
      time 2020
      icon mingcute/rocket-fill
    - label 2021
      desc Launched digital platform, improved internal operations
      time 2021
      icon mingcute/computer-line
    - label 2022
      desc Completed Series A funding, accelerated market expansion
      time 2022
      icon mingcute/receive-money-line
    - label 2024
      desc Advanced ecosystem partnerships, expanded national influence
      time 2024
      icon mingcute/world-2-line
theme
  palette antv
```

### 2. Sequence Infographics

Sequence data emphasizes order. Used for timelines, process steps, workflows.

**Data key:** `sequences` (or `items`)

```
infographic sequence-steps-simple
data
  title Content Publishing Review Process
  desc Standard pipeline from submission to publication (with rejection loop)
  sequences
    - label Start
      desc Creator prepares to publish
      icon mingcute/play-circle-line
    - label Submit Content
      desc Fill in title, body, materials
      icon mingcute/edit-line
    - label Machine Review
      desc Political/pornography/copyright/quality detection
      icon mingcute/robot-line
    - label Manual Review
      desc Borderline content further judgment
      icon mingcute/user-search-line
    - label Publish
      desc Content visible to public
      icon mingcute/send-line
    - label Reject & Revise
      desc Return with reason
      icon mingcute/close-circle-line
    - label End
      desc Process closed
      icon solar/flag-linear
theme
  palette antv
```

**Descending order:**

```
infographic sequence-stairs-front-pill-badge
data
  title Job Level Sequence
  sequences
    - label P7
    - label P6
    - label P5
  order desc
theme
  palette antv
```

### 3. Hierarchy Infographics

Hierarchy data describes tree structures. Common for org charts, taxonomies, mind maps.

**Data key:** `root` (tree node with `children`)

**Mind map style** (nested tree):

```
infographic hierarchy-mindmap-compact-card
data
  title User Research
  desc Understand user needs and pain points to guide product design
  root
    label User Research
    icon mingcute/user-question-line
    value 100
    children
      - label Why users choose a music platform
        icon mingcute/music-2-ai-line
        value 80
        children
          - label How users discovered this platform
            icon mingcute/ad-circle-line
            value 70
          - label What aspects attracted users
            icon mingcute/mushroom-line
            value 65
      - label What scenarios users use the platform in
        icon mingcute/time-line
        value 75
        children
          - label What events trigger usage
            icon mingcute/calendar-time-add-line
            value 60
          - label What features used in each scenario
            icon mingcute/danmaku-line
            value 55
theme
  palette antv
```

**Org chart style** (multi-root with `items`):

```
infographic hierarchy-structure
data
  title System Layered Architecture
  desc Module and functional grouping at different layers
  root
    label Presentation Layer
    children
      - label Mini Program
      - label APP
      - label PAD
      - label Client
      - label WEB
  root
    label Application Layer
    children
      - label Core Module
        children
          - label Feature 1
          - label Feature 2
          - label Feature 3
      - label Basic Module
        children
          - label Feature 1
          - label Feature 2
          - label Feature 3
  root
    label Platform Layer
    children
      - label Module 1
        children
          - label Feature 1
          - label Feature 2
      - label Module 2
        children
          - label Feature 1
          - label Feature 2
theme
  palette antv
```

### 4. Comparison Infographics

Comparison data highlights side-by-side differences.

**Data key:** `compares` (or `items`)

**SWOT Analysis** (4 groups with children):

```
infographic compare-swot
data
  title SWOT Analysis
  desc Comprehensive analysis of internal and external factors for strategic planning
  compares
    - label Strengths
      children
        - label Leading R&D capability
        - label Complete supply chain system
        - label Efficient customer service
        - label Experienced management team
        - label Strong user reputation
        - label Stable product quality
    - label Weaknesses
      children
        - label Insufficient brand exposure
        - label Slow product line updates
        - label Single market channel
        - label High operational costs
        - label Low organizational decision efficiency
        - label Slowing user growth
    - label Opportunities
      children
        - label Accelerated digital transformation
        - label Expanding emerging markets
        - label Favorable policy driving industry growth
        - label Increasing intelligent application scenarios
        - label More cross-industry collaboration opportunities
        - label User consumption upgrade trend
    - label Threats
      children
        - label Increasing industry competition
        - label Rapidly changing user needs
        - label Lower market entry barriers
        - label Rising supply chain risks
        - label Growing data and security challenges
        - label Macroeconomic uncertainty
theme
  palette antv
```

**Binary Comparison (Pros vs Cons):**

```
infographic compare-binary-horizontal-simple-vs
data
  title Enterprise Pros and Cons
  desc Core advantages and areas for improvement
  compares
    - label Advantages
      children
        - label Strong Product R&D
          desc Technology leadership with independent innovation
        - label High Customer Retention
          desc Repurchase rate over 60%, good reputation
        - label Complete Service System
          desc Fast after-sales response, high satisfaction
    - label Disadvantages
      children
        - label Weak Brand Exposure
          desc Insufficient marketing, awareness needs improvement
        - label Narrow Channel Coverage
          desc Incomplete online channels, limited reach
        - label High Operational Costs
          desc Labor and logistics costs above industry average
theme
  palette antv
```

**Quadrant (4 items, no children):**

```
infographic quadrant-quarter-simple-card
data
  title Risk Control
  desc Risk frequency and loss severity analysis
  compares
    - label High Loss, High Frequency
      desc Avoid risk directly
      icon mingcute/currency-bitcoin-2-fill
    - label Low Loss, High Frequency
      desc Take risk control measures
      icon mingcute/currency-bitcoin-fill
    - label High Loss, Low Frequency
      desc Transfer risk through insurance
      icon mingcute/dogecoin-doge-fill
    - label Low Loss, Low Frequency
      desc Choose to accept the risk
      icon mingcute/exchange-bitcoin-fill
theme
  palette antv
```

### 5. Relation Infographics

Relation data describes node-to-node connections. Used for flowcharts, networks, system diagrams.

**Data key:** `nodes` + `relations`

**Flowchart with Mermaid-style relations:**

```
infographic relation-dagre-flow-tb-simple-circle-node
data
  title Content Review Process
  desc Standard pipeline from submission to publication
  nodes
    - id start
      label Start
      icon mingcute/play-circle-line
    - id submit
      label Submit Content
      icon mingcute/edit-line
    - id auto
      label Machine Review
      icon mingcute/robot-line
    - id manual
      label Manual Review
      icon mingcute/user-search-line
    - id publish
      label Publish
      icon mingcute/send-line
    - id reject
      label Reject & Revise
      icon mingcute/close-circle-line
    - id end
      label End
      icon solar/flag-linear
  relations
    start -> submit
    submit -> auto
    auto -> publish
    auto -> manual
    auto -> reject
    manual -> publish
    manual -> reject
    reject -> submit
    publish -> end
theme
  palette antv
```

**System diagnosis flowchart** (with edge labels):

```
infographic relation-dagre-flow-tb-simple-circle-node
data
  title System Performance Diagnosis
  nodes
    - id 0
      label Check I/O wait (top)
      group pre-inspection
    - id 1
      label Check swap (free-m)
      group pre-inspection
    - id 2
      label Check % CPU (top)
      group pre-inspection
    - id 3
      label RAM PROBLEM
      group problem
    - id 4
      label I/O
      group problem
    - id 5
      label APP PROBLEM
      group problem
    - id 6
      label CPU PROBLEM
      group problem
    - id 7
      label What is hogging RAM? (top)
      group inspection
    - id 8
      label Check history - Is usage an anomaly?
      group inspection
    - id 9
      label Kill processes
      group solution
    - id 10
      label Infrastructure problem - add RAM
      group solution
    - id 11
      label What is hogging IO? (iotop)
      group inspection
    - id 12
      label Look for external dependency (strace)
      group inspection
    - id 13
      label Confirm CPU % user time (top)
      group inspection
    - id 14
      label Check process list (top)
      group inspection
    - id 15
      label Check history - Is usage an anomaly?
      group inspection
    - id 16
      label Kill processes
      group solution
    - id 17
      label Infrastructure problem - add cores
      group solution
  relations
    0 - HIGH -> 1
    0 - LOW -> 2
    1 - HIGH -> 3
    1 - LOW -> 4
    2 - HIGH -> 5
    2 - LOW -> 6
    3 -> 7
    7 -> 8
    8 - YES -> 9
    8 - NO -> 10
    4 -> 11
    5 -> 12
    6 -> 13
    13 -> 14
    14 -> 15
    15 - YES -> 16
    15 - NO -> 17
theme
  palette antv
```

**Network with bidirectional edges:**

```
infographic relation-network-icon-badge
data
  title Subsidiary Profit Analysis
  desc Financial performance of subsidiaries, profit growth YoY
  nodes
    - id hq
      label Group HQ
      desc Unified fund allocation and strategic planning
      value 128
      icon mingcute/building-4-line
    - id north
      label North Branch
      desc Manufacturing and warehousing base
      value 86
      icon mingcute/factory-line
    - id east
      label East Branch
      desc Core customer concentration area
      value 112
      icon icomoon-free/office
    - id south
      label South Branch
      desc Cross-border business growing fast
      value 95
      icon mingcute/earth-line
    - id west
      label Southwest Branch
      desc Emerging market cultivation
      value 64
      icon mingcute/mountain-line
    - id rd
      label R&D Center
      desc Product iteration and tech breakthrough
      value 78
      icon mingcute/flask-line
    - id supply
      label Supply Chain Center
      desc Procurement coordination and cost control
      value 72
      icon mingcute/truck-line
    - id marketing
      label Marketing Center
      desc Brand and channel growth
      value 88
      icon mingcute/speaker-line
    - id overseas
      label Overseas Division
      desc Regional expansion and partnerships
      value 69
      icon mynaui/plane
  relations
    hq -> north
    hq -> east
    hq -> south
    hq -> west
    hq -> rd
    hq -> supply
    hq -> marketing
    hq -> overseas
    rd -> east
    supply -> north
    marketing -> south
    overseas -> east
theme
  palette antv
```

**TCP Handshake (interaction diagram):**

```
infographic relation-dagre-flow-tb-simple-circle-node
data
  title TCP Three-Way Handshake
  desc Process of establishing a reliable connection between client and server
  nodes
    - id client-closed
      label CLOSED
      icon mingcute/close-circle-line
    - id client-syn-sent
      label SYN-SENT
      icon mingcute/send-line
    - id client-established
      label ESTABLISHED
      icon mingcute/check-circle-line
    - id server-closed
      label CLOSED
      icon mingcute/close-circle-line
    - id server-listen
      label LISTEN
      icon mingcute/ear-line
    - id server-syn-rcvd
      label SYN-RCVD
      icon mingcute/receive-line
    - id server-established
      label ESTABLISHED
      icon mingcute/check-circle-line
  relations
    client-closed - SYN=1, seq=x -> server-listen
    server-listen - SYN=1, ACK=1, seq=y, ack=x+1 -> client-syn-sent
    client-syn-sent - ACK=1, seq=x+1, ack=y+1 -> server-syn-rcvd
    client-established <-> server-established
theme
  palette antv
```

### 6. Statistics / Chart Infographics

Statistics data showcases metrics using `values`.

**Data key:** `values` (or `items`)

**Column chart:**

```
infographic chart-column-simple
data
  title Annual Revenue Growth
  desc Revenue comparison over past three years and this year target (unit: 100M)
  values
    - label 2021
      value 120
      desc Early transition phase, steady testing
      icon lucide/sprout
    - label 2022
      value 150
      desc Platform optimization, efficiency significantly improved
      icon lucide/zap
    - label 2023
      value 190
      desc Deep digital-intelligent integration, comprehensive growth
      icon lucide/brain-circuit
    - label 2024
      value 240
      desc Expand ecosystem synergy,冲击 new high
      icon lucide/trophy
theme
  palette antv
```

**Pie chart:**

```
infographic chart-pie-plain-text
data
  title Traffic Sources
  values
    - label Search
      value 62
    - label Direct
      value 38
theme
  palette antv
```

**Word cloud** (items as `label:value` pairs in a single string, or as array):

```
infographic word-cloud-simple
data
  values
    - label Data Analysis
      value 100
    - label AI
      value 96
    - label Data Visualization
      value 92
    - label Big Data
      value 90
    - label Machine Learning
      value 88
    - label Deep Learning
      value 84
    - label Data Engineering
      value 82
    - label Data Warehouse
      value 80
    - label Data Mining
      value 78
    - label Business Intelligence
      value 76
theme
  palette antv
```

---

## Design Section

The `design` section overrides template defaults.

| Key | Type | Description |
|---|---|---|
| `structure` | string \| object | Structure type, or `{ type, ...props }` |
| `item` | string \| object | Single item type for all data points |
| `items` | array | Per-level item types (for hierarchies) |
| `title` | string \| object | Title component type and config |

### Examples

```
# Override structure only
design
  structure list-row
    gap 20
    zigzag true

# Override item with config
design
  item simple-horizontal-arrow
    showIcon true

# Title config
design
  title default
    align-horizontal left
    desc-line-number 2

# Multi-level hierarchy items
design
  items
    - circle-node
    - pill-badge
```

> When both `item` and `items` exist, `items` has higher priority.

## Theme Section

### Shorthand — Theme Name Only

```
theme default
theme dark
theme hand-drawn
```

### Override Named Theme

```
theme dark
  colorPrimary #61DDAA
  colorBg #1F1F1F
  palette
    - #61DDAA
    - #F6BD16
    - #F08BB4
```

### Full Theme Config

```
theme
  colorPrimary: '#1677ff'
  palette: ['#1677ff', '#00C9C9', '#F0884D', '#D580FF']

  base
    text
      fill: '#333'
      font-family: 'Alibaba PuHuiTi'
    shape
      fill: '#fff'
      stroke: '#1677ff'

  title
    font-size: 24
    fill: '#1677ff'
  desc
    font-size: 14
    fill: '#666'

  item
    label
      font-size: 16
    desc
      font-size: 12
    icon
      fill: '#1677ff'

  stylize
    type: rough
    roughness: 2
    bowing: 1
```

### Stylize Config

| Key | Type | Description |
|---|---|---|
| `type` | `rough` \| `pattern` \| `linear-gradient` \| `radial-gradient` | Stylization type |
| `roughness` | number | Roughness level (rough, 0-10) |
| `bowing` | number | Bowing of lines (rough) |
| `fillWeight` | number | Fill stroke weight (rough) |
| `hachureGap` | number | Hatch gap (rough) |
| `pattern` | string | Pattern name: `dot`, `line`, `square`, `diamond`, `hex`, `mosaic` |
| `backgroundColor` | color | Pattern background |
| `foregroundColor` | color | Pattern foreground |
| `scale` | number | Pattern scale |
| `angle` | number | Gradient angle (0-360, linear-gradient) |
| `colors` | array | Gradient color stops |

## Relation Edge Syntax (Mermaid-style)

| Syntax Example | Description |
|---|---|
| `A -> B` | from A to B |
| `A <- B` | from B to A |
| `A -- B` | undirected edge (`direction none`) |
| `A<->B` | bidirectional edge (`direction both`) |
| `A -relation label-> B` | relation label (no special characters) |
| `A -->\|relation label\| B` | relation label (allows special characters) |
| `A --> B[label]` | node label (`label`) |

**Notes:**
- Extra dashes (e.g. `A ----> B`), `-.-`, `==>`, `--x`, `--o` are normalized to `--` or `->`.
- `id1(label)` / `id1([label])` are equivalent to `id1[label]`.
- Attributes like `id@{...}` are ignored.

### Relation Edge Fields (explicit format)

| Key | Type | Required | Description |
|---|---|---|---|
| `id` | string | No | Custom edge id |
| `from` | string | **Yes** | Source node id |
| `to` | string | **Yes** | Target node id |
| `label` | string | No | Edge label text |
| `direction` | `forward` \| `both` \| `none` | No | Direction (default: `forward`) |
| `showArrow` | boolean | No | Show arrowheads |
| `arrowType` | `arrow` \| `triangle` \| `diamond` | No | Arrow style |

## Syntax Error Codes

| Code | Meaning |
|---|---|
| `implicit_template` | Template inferred from bare first line (warning) |
| `unknown_key` | Unrecognized key at current level |
| `schema_mismatch` | Value type doesn't match expected schema |
| `invalid_value` | Value fails validation (e.g., bad color, bad enum) |
| `bad_indent` | Inconsistent or invalid indentation |
| `bad_list` | List item (`-`) not under an array context |
| `bad_syntax` | Unparseable line |

## Parsing API

```ts
import { parseSyntax } from '@antv/infographic';

const result = parseSyntax(input);
// result.options  — Partial<InfographicOptions>
// result.errors   — SyntaxError[]
// result.warnings — SyntaxError[]
// result.ast      — ObjectNode (raw AST)
```
