# Trading Agent — later release

[Documentation index](../README.md)

> Target architecture derived from Project PT specification v3.0, November 2026. These are planned capabilities unless explicitly stated otherwise.

Purpose: Analyze trading systems and expose decision-support information, initially without execution rights.

| Module                 | Responsibility                         |
| ---------------------- | -------------------------------------- |
| Backtest analyzer      | Returns, drawdowns, trade statistics   |
| Risk engine            | Position sizing, exposure, loss limits |
| Strategy evaluator     | In-sample and out-of-sample comparison |
| Monte Carlo engine     | Simulated equity-path distributions    |
| Trade journal          | Execution history and trade tagging    |
| Market data connector  | Approved historical and live feeds     |
| OrbCatcher integration | Read-only EA reports and monitoring    |

For your OrbCatcher system, PT could compare two strategy configurations, calculate risk-adjusted metrics, examine losing streaks, and generate structured reports.

Live order execution is outside the initial Trading Agent's scope. If added, it would need separate authorization, independent pre-trade risk checks, auditability, and a fail-closed execution service. The LLM should never have unrestricted direct access to MT5 trading commands.
