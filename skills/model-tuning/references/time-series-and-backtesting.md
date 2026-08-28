# Time series and backtesting

Load for ordered forecasting, temporal validation, market regimes, signal/policy evaluation, or execution-aware simulation.

Use chronological, expanding-window, or rolling-window validation. Fit preprocessing within each training split. Keep validation/test periods isolated from feature and model-selection decisions. Evaluate across multiple regimes and report period sensitivity.

Separate layers: predictive forecast evaluation -> explicit versioned signal/policy mapping -> execution-aware simulation. Report forecast quality, signal quality, strategy performance, and executable-performance assumptions separately. Backtests must use point-in-time contract/roll/calendar/price data supplied by data engineering and reject future-known fills, costs, contract choices, revisions, or policy changes.

This is hypothetical evaluation only. It never grants deployment, order submission, position sizing authority, or live trading permission.
