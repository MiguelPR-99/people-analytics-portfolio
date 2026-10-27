# Metrics and calculation rules

[← Back to the case](../README.en.md) · [Español](metric-dictionary.md)

## Population and context

Calculations use synthetic reviews. Unless otherwise stated, percentages use reviewed employees within the active filters as their denominator. Employee counts use distinct `EmployeeID`.

Review period, department, and other filters can change both the result and its benchmark. Before comparing two views, check that they represent the same population and period.

## Ratings and the 9-box matrix

| Concept | Rule |
|---|---|
| Performance | Assigned review level: Low, Moderate, or High |
| Potential | Assigned review level: Low, Moderate, or High |
| 9-box position | Cell matching the performance and potential combination |
| Future Leader | High performance and high potential |
| Under Performer | Low performance and low potential |
| Future Leader % | Distinct employees in that cell / distinct reviewed employees |
| Under Performer % | Distinct employees in that cell / distinct reviewed employees |

The report receives these assessments; it does not calculate performance or predict potential from other attributes. *Future Leader* and *Under Performer* are exercise labels for specific combinations, not permanent descriptions of a person.

## Movement between reviews

The selected period is compared with the immediately preceding available review.

| Report classification | Rule |
|---|---|
| Improved | Performance or potential rises, with no decrease in the other |
| Stable | The matrix position stays the same |
| Declined | Performance or potential falls, with no increase in the other |
| Mixed | Performance and potential move in opposite directions |
| Transition count | Distinct employees for each previous/current position combination |

The first available review has no prior comparison and returns a blank classification. A missing comparison does not mean stability.

For example, moving from moderate performance and high potential to high performance and moderate potential is mixed movement. The display order of 9-box labels is not treated as a single improvement scale.

In the 2025–2026 example, the classifications are 66% Stable, 18% Improved, 14% Declined, and 2% Mixed. They describe changes in recorded assessments without establishing their causes or objective changes in people's capabilities.

## Calibration across managers

| Metric | Rule |
|---|---|
| Manager average | Average performance or potential score for the manager's reviewed employees under the active filters |
| Selected-population benchmark | Corresponding average across all managers retained by the report filters |
| Performance gap | Manager average performance − selected-population average performance |
| Potential gap | Manager average potential − selected-population average potential |
| Calibration signal | Absolute value of either gap ≥ 0.25 points **and** at least five reviewed employees per manager |

A positive gap means the average is above the benchmark; a negative gap means it is below. Bubble size represents reviewed employees. Gaps are score-point differences, not percentages.

The 0.25 threshold and minimum of five employees are exercise rules. They are not universal standards, significance tests, or sufficient safeguards for small groups. Their statistical validity has not been established.

Differences can guide discussions about criteria, evidence, or team composition. They do not establish bias, discrimination, or management quality. Being within range does not establish that criteria were applied correctly either.

The calibration screenshot uses **2024**: three of eight managers meet the rule in that selection. This is a different period from the 2025–2026 movement comparison.

## Department Talent Balance

**Talent Balance = Future Leader % − Under Performer %.**

This is a difference in **percentage points**. A positive value means a larger share in Future Leader; a negative value means a larger share in Under Performer. The indicator summarizes those two cells and leaves out the other seven.

For Customer Success in 2026, there are six employees: none in Future Leader and three in Under Performer. The calculation is **0% − 50% = −50 percentage points**. One person represents approximately 16.7 percentage points in a group of that size.

The screenshot retains percentage formatting and a headline about *talent risk* and *pipeline strength*. These terms should not be read as predictive risk, attrition probability, overall talent quality, or demonstrated leadership readiness. They do not independently justify department rankings or individual decisions.
