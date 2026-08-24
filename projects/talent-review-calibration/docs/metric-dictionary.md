# Metric dictionary

## Scope

All calculations use synthetic employee review data. Percentages use the reviewed population in the active filter context unless otherwise noted.

## Talent position

| Metric | Business rule |
|---|---|
| Performance | Low, Moderate, or High score assigned for the selected review period |
| Potential | Low, Moderate, or High score assigned for the selected review period |
| Talent position | Named cell produced by the performance/potential combination |
| Future Leader | High performance and High potential |
| Under Performer | Low performance and Low potential |
| Future Leader % | Distinct employees in Future Leader divided by distinct reviewed employees |
| Under Performer % | Distinct employees in Under Performer divided by distinct reviewed employees |

## Movement

Movement compares the selected review period with the immediately preceding available review.

| Classification | Business rule |
|---|---|
| Improved | Positive movement in performance or potential with no offsetting negative movement |
| Stable | Same talent position in current and prior review |
| Declined | Negative movement in performance or potential with no offsetting positive movement |
| Mixed | Performance and potential move in opposite directions |
| Transition count | Distinct employees for each prior-to-current talent-position combination |

The first available review period has no prior comparison and therefore returns no movement classification.

## Calibration

| Metric | Business rule |
|---|---|
| Manager average performance | Average employee performance score for one manager in the active filter context |
| Manager average potential | Average employee potential score for one manager in the active filter context |
| Selected-population benchmark | Corresponding average for all managers retained by the active report filters |
| Performance gap | Manager average performance minus selected-population average performance |
| Potential gap | Manager average potential minus selected-population average potential |
| Calibration signal | Absolute performance or potential gap is at least 0.25 points and the manager has at least five reviewed employees |

Signals identify cases for discussion. They do not prove rating bias or manager quality.

## Department analysis

| Metric | Business rule |
|---|---|
| Department employees | Distinct reviewed employees in the department |
| Talent Balance | Future Leader % minus Under Performer % |
| Positive Talent Balance | Leadership-pipeline share exceeds under-performer share |
| Negative Talent Balance | Under-performer share exceeds leadership-pipeline share |

Percentage-point differences should be interpreted with department size and organizational context.
