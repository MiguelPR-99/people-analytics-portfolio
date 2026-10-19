# Project 2: HR Policy & Services Agent

A Digital HR case built with Microsoft Copilot Studio and Power Automate to answer policy questions with evidence and turn requests that need follow-up into synthetic HR Services tickets.

[← Back to portfolio](../../README.md) · [Español](README.es.md)

![Copilot Studio](https://img.shields.io/badge/Copilot%20Studio-5C2D91?logo=microsoftcopilot&logoColor=white)
![Power Automate](https://img.shields.io/badge/Power%20Automate-0066FF?logo=powerautomate&logoColor=white)
![Microsoft Lists](https://img.shields.io/badge/Microsoft%20Lists-0078D4?logo=microsoftlists&logoColor=white)
![Microsoft 365](https://img.shields.io/badge/Microsoft%20365-D83B01?logo=microsoftoffice&logoColor=white)

> Independent portfolio project. It is not an official system and is not affiliated with or endorsed by Siemens Energy. All policies, people, requests, and results are synthetic.

## Executive summary

The agent addresses two common HR Services needs:

1. Answer questions about leave, benefits, onboarding, and HR documents with verifiable citations.
2. Create a service request when the user needs human follow-up, without collecting unnecessary sensitive information.

The solution combines configured-document retrieval, responsible-use instructions, a Power Automate flow, and Microsoft Lists. Before creating a ticket, it displays a summary and requires explicit confirmation.

## End-to-end demonstration

This one-minute walkthrough shows the complete experience: a benefits question is answered with retrieved evidence; the agent then collects only synthetic details, presents a summary, waits for explicit confirmation, and creates the request through Power Automate. The result includes a ticket number, service, status, and target dates, and is stored in Microsoft Lists.

![End-to-end demonstration of the HR Policy & Services Agent](assets/demo/hr-policy-services-agent-demo.gif)

[Open the MP4 demonstration](assets/demo/hr-policy-services-agent-demo.mp4)

The recording provides four observable pieces of evidence:

- **Grounding:** it retrieves `EPS-SYN-POL-002` and preserves the section used.
- **Action control:** it presents the request details and waits for confirmation in a later message.
- **Execution:** Power Automate returns structured output with the ticket, service, status, and SLA.
- **Traceability:** the new request appears in Microsoft Lists.

Every name, email address, and record shown is synthetic.

## What the project solves

- Reduces manual policy lookup while preserving the source used.
- Recognizes when available evidence is insufficient.
- Keeps the conversation in English or Spanish according to the user's message.
- Refuses requests for individual salary, performance, or medical information.
- Routes sensitive matters to human review through `ESC-01`.
- Validates the requested service and creates a ticket with priority, queue, and target dates.

## Supporting evidence

The following screenshots provide a closer look at the controls represented in the demonstration.

### Evidence-grounded answer

The agent retrieves the relevant document, answers the question, and identifies the section used.

![Evidence-grounded answer with citations](assets/screenshots/grounded-policy-answer.png)

### Restricted-data protection

Requests for individual salary, performance ratings, or medical information are refused without attempting to retrieve or infer those data.

![Restricted-data protection](assets/screenshots/privacy-guardrail.png)

## How it works

```mermaid
flowchart LR
    U[User] --> A[Copilot Studio agent]
    A --> K[Synthetic policy PDFs]
    K --> A
    A -->|Cited answer| U
    A -->|Follow-up required| C[Summary and confirmation]
    C -->|Explicit confirmation| F[Power Automate]
    F --> S[Service catalog]
    F --> R[HR Service Requests]
    R --> A
    A -->|Ticket and SLA| U
```

1. Copilot Studio interprets the question and searches four synthetic policy documents.
2. When evidence is sufficient, it answers with the document and section.
3. When evidence is missing or the case needs a person, it offers to create a request.
4. The agent collects only synthetic details and a non-sensitive summary.
5. After confirmation, Power Automate validates the service, calculates target dates, and stores the ticket.

[Read the architecture and control notes](docs/architecture.md)

## Evaluation

The final test set contains 15 scenarios covering policy retrieval, missing evidence, privacy, escalation, and language behavior.

| Result | Value |
|---|---:|
| Cases executed | 15/15 |
| General quality | 12/15 · 80% |
| Semantic similarity | 15/15 · 100% |
| Bilingual questions | Passed |

The three general-quality failures are intentional refusals: remote-work policy without evidence, restricted personal data, and an individual legal or medical determination. All three matched the expected safe response.

[Review the evaluation method, results, and limitations](docs/evaluation-report.md)

## Main iterations

- A duplicate OneDrive source caused connection prompts during automated evaluation. It was removed while the directly uploaded PDFs were retained.
- The language rule was moved near the beginning of the instructions and a final language check was added.
- The bilingual test made its expected response language explicit. Semantic similarity improved from 93% to 100%.

## Resources

- [Animated demonstration](assets/demo/hr-policy-services-agent-demo.gif)
- [Video demonstration](assets/demo/hr-policy-services-agent-demo.mp4)
- [Final agent instructions](prompts/agent-instructions.txt)
- [Test cases](evaluation/test-cases.csv)
- [Complete evaluation results](evaluation/final-results.csv)
- [Synthetic knowledge documents](knowledge/)
- [Architecture and controls](docs/architecture.md)
- [Evaluation report](docs/evaluation-report.md)

## Tools

- Microsoft Copilot Studio
- Power Automate
- Microsoft Lists
- Microsoft 365
- Copilot Studio integrated evaluation

## Responsible use

- The agent does not access real employee data or internal company systems.
- Accepted demonstration emails must use `@example.com`.
- It does not request, reveal, or infer salary, individual performance, or medical information.
- Sensitive matters require human review; the agent does not investigate or make employment decisions.
- Ticket creation requires explicit confirmation and uses synthetic data only.

## Author

Miguel — [GitHub profile](https://github.com/MiguelPR-99)
