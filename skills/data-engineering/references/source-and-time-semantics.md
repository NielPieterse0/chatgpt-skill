# Source and time semantics

Load for historical, revised, commodity, futures, weather, or other time-sensitive sources.

- Record source provenance, immutable snapshot/version, schema, freshness, access constraints, units, timezone, and source-native timestamps.
- Separate observation, publication/release, ingestion, and decision timestamps. Historical features may use only information available by the decision cutoff.
- Preserve revision/vintage identity. Weather forecasts require issue/vintage time; later observed weather is not a historical forecast feature. Fundamental releases must respect actual publication lag.
- Futures data must preserve contract, expiry, exchange/session calendar, timezone, and source timestamps. Continuous series must record roll rule, adjustment method, roll dates, and underlying contracts; never treat a synthetic series as exchange-traded.
- Term-structure features may use only contracts and quotes available at the information cutoff.
