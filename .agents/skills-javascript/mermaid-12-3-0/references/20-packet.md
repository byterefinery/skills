# Packet diagrams

Keyword: `packet`. Illustrates network packet structure as bit fields.

Sources: `docs/syntax/packet.md` at mermaid@12.3.0.

## Syntax

Each line after the optional `title`: `<range>: "Field name"` where the range is `start-end` (e.g. `0-15`), a single bit (`106`), or a relative bit count `+<count>` (v11.7.0+) starting from the end of the previous field. Forms can be mixed.

```mermaid
packet
title UDP Packet
+16: "Source Port"
+16: "Destination Port"
32-47: "Length"
48-63: "Checksum"
64-95: "Data (variable length)"
```

## Bit numbering (v12.0.0+)

Rows are numbered lowest bit left → highest bit right (network convention). Set `packet: { bitOrder: descending }` to mirror every row (hardware-register convention, MSB left). Fields are still declared lowest bit first (`0-7`, never `7-0`); each row is mirrored independently (with default `bitsPerRow: 32`, the second row runs from bit 63 down to 32).

```mermaid
---
config:
  packet:
    showBits: true
    bitOrder: descending
    bitsPerRow: 16
---
packet
0-7: "DATA"
8-11: "TYPE"
12: "EN"
13-15: "RESERVED"
```

## Verified examples

TCP packet (docs):

```mermaid
packet
0-15: "Source Port"
16-31: "Destination Port"
32-63: "Sequence Number"
64-95: "Acknowledgment Number"
96-99: "Data Offset"
100-105: "Reserved"
106: "URG"
107: "ACK"
108: "PSH"
109: "RST"
110: "SYN"
111: "FIN"
112-127: "Window"
128-143: "Checksum"
144-159: "Urgent Pointer"
160-191: "(Options and Padding)"
192-255: "Data (variable length)"
```
