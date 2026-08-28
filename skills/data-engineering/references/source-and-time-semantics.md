# Source and time semantics

Load for historical, revised, commodity, futures, weather, event, publication-driven, or other time-sensitive sources.

## Time axes
Do not collapse distinct time concepts into one generic timestamp. Record the axes that matter for the decision:

- **observation/event time:** when the underlying event or measurement occurred;
- **publication/availability time:** when the value first became knowable to the intended decision maker;
- **revision/vintage time:** which published version of a value is represented;
- **ingestion time:** when the pipeline acquired the value;
- **processing time:** when a transformation ran, if operational sequencing matters;
- **decision/information-cutoff time:** the latest information a historical decision is allowed to use.

Point-in-time correctness requires every historical feature to be derivable from information available no later than its decision cutoff. Later truth is useful for evaluation or remediation, but it is not a valid substitute for what was historically knowable.

## Availability and missingness states
When time or source reliability matters, preserve the reason a value is absent. Useful states include:

- `not_applicable`: the field does not apply to this entity/event;
- `not_observed`: the phenomenon could have been observed but no observation exists;
- `not_yet_published` (**not yet published**): the value exists conceptually but was not available by the decision cutoff;
- `source_unavailable` (**source unavailable**): retrieval or source-system failure prevented acquisition;
- `suppressed_or_redacted`: policy or source rules intentionally withhold the value;
- `invalid_or_rejected`: a value was present but failed an explicit validity rule.

Do not silently map these states to numeric zero, an empty string, forward-fill, or an imputed estimate. If a storage format cannot encode the state directly, carry an explicit status/provenance field or equivalent contract metadata.
## Revisions and vintages
For revised statistics, forecasts, fundamentals, reference data, or corrected events:

- preserve source version/vintage identity;
- retain the first-known value when historical reproducibility requires it;
- record correction/revision timestamps and policies;
- never backfill a historical feature with a later revision unless the study explicitly models revised-information availability;
- distinguish a replay using historical vintages from a reconstruction using today's latest source.

A bitemporal representation can be useful when both valid/event time and system/knowledge time matter, but do not impose one database design when explicit versioned snapshots provide the same auditability.

## Timezone, calendar, and session rules
Store source timezone and normalize only with a documented rule. Preserve daylight-saving transitions, market-session calendars, holidays, publication calendars, and period-end conventions where they affect availability or aggregation. A date without its timezone/calendar semantics is often insufficient evidence.

For rolling windows and aggregations, define whether boundaries are open/closed and whether the current observation is included. Verify edge cases at daylight-saving changes, month/quarter boundaries, market opens/closes, and irregular publication times.

## Market and futures data
For futures, preserve contract identifier, exchange, expiry, session calendar, quote/trade timestamp, price type, and source. A continuous series is synthetic: record the roll rule, roll dates, adjustment method, and underlying contracts. Do not treat a back-adjusted continuous price as an exchange-traded executable price.

Term-structure, carry, curve, and roll features may use only contracts and quotes actually available at the information cutoff. Contract selection based on future volume/open-interest realizations is look-ahead unless the historical selection rule is reconstructed point-in-time.

Weather forecasts, analyst estimates, macro releases, and similar forecasts require issue/publication vintage. Later realized weather or revised macro data cannot replace the historical forecast in a point-in-time feature set.

## Verification questions
- Can every historical row identify the information cutoff applied to it?
- Can the reviewer tell whether a value was observed, published, revised, or merely ingested at each timestamp?
- Are missing values distinguishable from values not yet available?
- Do joins use the latest *available* record rather than the latest record that now exists?
- Are timezone, session, and roll rules deterministic and versioned?
