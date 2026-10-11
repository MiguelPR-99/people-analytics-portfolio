# Evaluation report

[← Back to case study](../README.md) · [Español](evaluation-report.es.md)

## Objective

Verify that the agent answers with evidence when appropriate, abstains when evidence is unavailable, protects restricted information, follows the requested language, and retains human review for sensitive matters.

## Design

- Type: single response.
- Test cases: 15.
- Methods: general quality and semantic similarity.
- Similarity passing score: 50.
- Profile: authenticated user with required connections.
- Sources: four directly uploaded synthetic PDFs.

Cases cover leave, benefits, onboarding, documents, missing evidence, privacy, sensitive matters, and questions in Spanish and English.

## Final result

| Method | Passed | Result |
|---|---:|---:|
| General quality | 12 of 15 | 80% |
| Semantic similarity | 15 of 15 | 100% |

## Interpretation of the three quality failures

The general-quality evaluator classified three responses as “unanswered” because the agent declined to provide a direct answer:

1. A remote-work policy not contained in the configured sources.
2. Individual salary, performance-rating, and medical information.
3. An individual country-specific statutory-leave or medical-eligibility determination.

These refusals are expected behavior. All three passed semantic similarity because they matched the safe response defined in the test set.

The 80% score therefore does not represent three factual errors. It reflects a limitation of the general evaluator when grading responses that are required to abstain by design.

## Test evolution

| Run | Quality | Similarity | Observation |
|---|---:|---:|---|
| Initial | 33% | — | A OneDrive source requested a connection during the batch |
| After configuring the connection | 27% | 20% | The automated evaluation still showed the prompt |
| After removing the duplicate source | 80% | 87% | Direct-PDF retrieval worked |
| Reinforced bilingual rule | 80% | 93% | One English case still answered in Spanish during the batch |
| Explicit language criterion | 80% | 100% | Final result |

## Limitations

- Integrated evaluation uses AI graders; safe-refusal quality results require human interpretation.
- The demonstration uses synthetic policies and records and does not measure accuracy against real company policies.
- The exported file retains full detail for audit. Its first response is duplicated in the exported text, although both methods scored it as passed.
- Evaluation does not replace the security, compliance, and performance testing required for production.

## Files

- [Test cases](../evaluation/test-cases.csv)
- [Final results](../evaluation/final-results.csv)
