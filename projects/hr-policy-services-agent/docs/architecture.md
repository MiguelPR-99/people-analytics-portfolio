# Architecture and controls

[← Back to case study](../README.md) · [Español](architecture.es.md)

## Components

| Component | Responsibility |
|---|---|
| Copilot Studio | Orchestrates conversation, knowledge retrieval, rules, and tool use |
| Four synthetic PDFs | Provide leave, benefits, onboarding, and HR-document policy content |
| Power Automate | Validates the service, generates the ticket, calculates targets, and creates the record |
| HR Service Catalog | Defines applicable code, service, priority, queue, and SLA |
| HR Service Requests | Stores synthetic requests and their operational status |
| Copilot Studio evaluation | Runs repeatable questions and compares responses with expected outcomes |

## Knowledge flow

The agent answers only when configured sources contain sufficient evidence. Its response preserves the retrieved citation and identifies the document and section. When evidence is unavailable, it does not fill the gap with general knowledge; it offers human review.

Knowledge sources are directly uploaded files. A duplicate OneDrive source was removed during testing because it introduced a connection prompt in automated evaluation.

## Request-creation flow

1. The user selects or provides a service code.
2. The agent obtains a non-sensitive summary, synthetic name, `@example.com` email, and contact-consent choice.
3. It displays the data and asks for confirmation.
4. It waits for a new message; contact consent does not count as creation confirmation.
5. Power Automate validates the code against the active catalog.
6. The flow generates `TicketNumber`, priority, queue, status, and first-response and resolution targets.
7. The agent displays only values returned by the tool.

## Main controls

| Risk | Implemented control |
|---|---|
| Unsupported answer | Evidence requirement and explicit insufficient-evidence response |
| Incorrect citation | Only a document actually retrieved can be cited |
| Action without authorization | Summary, confirmation question, and wait for a new message |
| Duplicate tickets | One tool call per explicit confirmation |
| Real personal data | Synthetic names and mandatory `@example.com` domain |
| Restricted information | No requesting, revealing, or inferring individual salary, performance, or medical data |
| Sensitive matter | `ESC-01` routing and human review |
| False service promise | Only SLA values returned by the tool are communicated |

## Technical scope

This repository documents the design and provides synthetic data, instructions, results, and visual evidence. Power Platform connections, tenant identifiers, and credentials are not published. The flow depends on authenticated connections in the deployment environment.
