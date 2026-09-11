## Experiment: Baseline - [02-09-2026 20:00]

**Representation:** header + text

- Hit@1: 20.0%
- Hit@3: 66.7%
- Hit@5: 93.3%

## Experiment: Double header - [02-09-2026 20:06]

**Representation:** `header + header + text`

- Hit@1: 20.0%
- Hit@3: 86.7%
- Hit@5: 93.3%

## Experiment: Triple header - [02-09-2026 20:19]

**Representation:** `header + header + header + text`

- Hit@1: 26.7%
- Hit@3: 86.7%
- Hit@5: 93.3%

## Experiment: Humanized pattern name - [02-09-2026 20:40]

**Representation:** `humanized pattern + double header + text`

- Hit@1: 26.7%
- Hit@3: 86.7%
- Hit@5: 93.3%

## Experiment: Double header - [02-09-2026 20:51]

**Representation:** `header + header + text`

- Hit@1: 20.0%
- Hit@3: 86.7%
- Hit@5: 93.3%

## Experiment: Post Mission 9 retrieval - [05-09-2026 16:03]

**Representation:** `current indexed chunks`

- Hit@1: 20.0%
- Hit@3: 73.3%
- Hit@5: 80.0%
- Total cases: 15

## Experiment: Custom Generation Baseline - [11-09-2026 14:05]

- Passed cases: 8
- Failed cases: 1
- Total cases: 9
- Pass rate: 88.9%

## Experiment: LangChain Generation - [11-09-2026 14:05]

- Passed cases: 8
- Failed cases: 1
- Total cases: 9
- Pass rate: 88.9%

## Experiment: LLM Fallback End-to-End Latency - [11-09-2026 14:42]

### Custom
- Average: 3.367 s
- Minimum: 0.992 s
- Maximum: 6.558 s
- Runs: 10

### LangChain
- Average: 3.123 s
- Minimum: 0.615 s
- Maximum: 5.837 s
- Runs: 10

