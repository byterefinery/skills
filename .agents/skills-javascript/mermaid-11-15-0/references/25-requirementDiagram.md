# Requirement Diagrams

Requirement diagrams model system requirements and their relationships (SysML-style).

## Declaration

```mermaid
requirementDiagram
    requirement test_req {
        id: 1
        text: sample requirement
    }
```

## Basic Requirements

Define requirements with `id`, `text`, `risk`, and `verifymethod`. Link with relationship keywords.

```mermaid
requirementDiagram
    requirement SystemPerf {
        id: 1
        text: The system shall handle 1000 users
        risk: High
        verifymethod: Test
    }
    requirement UserAuth {
        id: 2
        text: Users must authenticate via SSO
        risk: Medium
        verifymethod: Inspection
    }
    SystemPerf - refines -> UserAuth
```

## Functional and Design Requirements

Use different requirement types.

```mermaid
requirementDiagram
    functionalRequirement Login {
        id: F1
        text: User can log in with email
        risk: Low
        verifymethod: Test
    }
    designConstraint TokenStore {
        id: D1
        text: JWT stored in httpOnly cookie
    }
    Login - satisfies -> TokenStore
```

## Elements and Relationships

Connect requirements to system elements with `satisfies`, `traces`, `verifies`, etc.

```mermaid
requirementDiagram
    element WebServer {
        type: Infrastructure
        docref: "nginx-config"
    }
    requirement HTTPS {
        id: S1
        text: All traffic over HTTPS
        risk: High
        verifymethod: Demonstration
    }
    WebServer - satisfies -> HTTPS
```

## Contains Relationships

Nest sub-requirements with `contains`.

```mermaid
requirementDiagram
    requirement ParentReq {
        id: P1
        text: System shall be secure
        risk: High
        verifymethod: Analysis
    }
    requirement ChildReq {
        id: C1
        text: Data encrypted at rest
        risk: Medium
        verifymethod: Inspection
    }
    ParentReq - contains -> ChildReq
```

## Multiple Relationship Types

Use `satisfies`, `contains`, `traces`, `verifies`, `refines`, `derives`, `copies`.

```mermaid
requirementDiagram
    requirement HighLevel {
        id: R1
        text: System processes orders
    }
    functionalRequirement ProcessOrder {
        id: R2
        text: Validate and process order
    }
    performanceRequirement FastResponse {
        id: R3
        text: Response under 500ms
    }
    HighLevel - contains -> ProcessOrder
    HighLevel - refines -> FastResponse
```
