# Packet Diagrams

Packet diagrams visualize the bit-level structure of network protocol packets.

## Declaration

```mermaid
packet
0-7: "Source Port"
8-15: "Dest Port"
```

## Basic Packet Structure

Define fields with bit ranges and labels. Use `start-end` for multi-bit, `bit` for single-bit.

```mermaid
---
title: "TCP Header"
---
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
```

## Bit Count Syntax (v11.7.0+)

Use `+<count>` to auto-increment from the previous field end.

```mermaid
packet
+16: "Source Port"
+16: "Destination Port"
+32: "Sequence Number"
+32: "Acknowledgment Number"
+4: "Data Offset"
+6: "Reserved"
+1: "URG"
+1: "ACK"
+1: "PSH"
+1: "RST"
+1: "SYN"
+1: "FIN"
+16: "Window"
```

## Mixed Syntax

Mix range-based and count-based definitions.

```mermaid
---
title: "IPv4 Header"
---
packet
+4: "Version"
+4: "IHL"
+8: "DSCP/ECN"
+16: "Total Length"
+16: "Identification"
+3: "Flags"
+13: "Fragment Offset"
+8: "TTL"
+8: "Protocol"
+16: "Header Checksum"
+32: "Source Address"
+32: "Destination Address"
```
