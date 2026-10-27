# Agent evaluation

[← Case study](../README.en.md) · [Español](evaluation-report.md)

The evaluation checks whether the agent answers policy questions, recognizes missing information, and follows privacy and language instructions. The final set contains fifteen single-turn questions. The conversation for creating a ticket is shown separately in the demonstration.

## What was evaluated

Questions cover leave, benefits, onboarding, HR documents, information missing from the sources, restricted personal data, sensitive matters, and answers in English and Spanish.

Copilot Studio's integrated evaluation was used with an authenticated user and four directly uploaded synthetic PDFs. Two methods were applied:

- **Answer quality:** the AI evaluator assesses the answer against its criteria.
- **Semantic similarity:** compares the answer with the expected response. The configured threshold was 50.

[Test questions and expected responses](../evaluation/test-cases.csv) · [Exported results](../evaluation/final-results.csv)

## Final result

| Method | Questions passed | Interpretation |
|---|---:|---|
| Answer quality | 12 of 15 (80%) | Three answers were classified as “unanswered.” |
| Semantic similarity | 15 of 15 (100% of the set) | All passed the configured criterion against the expected response. |

The 100% is the proportion of questions passing in this set. It does not mean the answers were identical to the expected responses or that the agent has 100% accuracy on any question.

## Why three answers did not pass the first method

The evaluator classified answers to these requests as “unanswered”:

1. A remote-work policy that was not included in the sources.
2. An individual's salary, performance, and medical information.
3. An individual country-specific statutory-leave or medical-eligibility determination.

In those cases, the expected behavior was not to provide the requested information. All three passed semantic similarity because they matched that expected outcome. The 80% is not interpreted here as three factual errors; the methods are assessing different aspects.

## Changes during evaluation

| Documented run | Quality | Similarity | Change or observation |
|---|---:|---:|---|
| Initial | 33% | — | A OneDrive source requested a connection during the batch. |
| After configuring the connection | 27% | 20% | Connection prompts persisted in automated evaluation. |
| After removing the duplicate source | 80% | 87% | Retrieval could use the directly uploaded PDFs. |
| Reinforced language instructions | 80% | 93% | One English question still received a Spanish answer. |
| Explicit language question | 80% | 100% | The question explicitly requested an entirely English answer. |

The history includes changes to configuration and instructions as well as one question. The difference between 93% and 100% is therefore not presented as an agent improvement measured with an identical test set.

The question CSV now retains the exact fifteen questions and expected responses found in the final export, including the language instruction in question 14. The exported results remain unchanged.

## What this demonstrates and what it does not cover

These tests provide evidence about answers to the fifteen published questions. The demonstration also shows one policy-lookup, confirmation, and ticket-creation flow. The fifteen questions are not fifteen complete tests of that flow.

AI graders require interpretation, particularly when abstention is expected. The first answer appears twice in the exported text; both methods classified it as passed.

The scenario uses synthetic policies and data. It does not measure behavior on any real policy or demonstrate time savings in an operation. It also does not replace additional conversation, security, or performance testing before production use.

[Watch the demonstration](../README.en.md#end-to-end-demonstration) · [Read the architecture](architecture.en.md)
