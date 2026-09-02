# Research evidence and source reconciliation

Load when reviewing why the specialist uses a particular contract, quality, temporal, missing-data, leakage, documentation, versioning, or reproducibility rule. This file is evidence context, not independent repository authority.

## Harvested specialist evidence
The upstream Data Engineer checked during issue #134 is:

- M. Sitarzewski, `agency-agents`, `engineering/engineering-data-engineer.md`: https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-data-engineer.md

Durable concepts retained from that source include explicit producer/consumer data contracts; source profiling; keys/cardinality; schema validation and evolution; deliberate null handling; lineage; idempotent pipelines; incremental/CDC processing; late-arriving data; units/currency normalization; observability; and explicit cost/latency trade-offs.

Repository adaptation deliberately does **not** inherit its persona, memory claims, product-specific technology preferences, universal SLA percentages, autonomous operational behavior, or rigid Bronze/Silver/Gold consumption rules. Those are source-specific implementation assumptions rather than portable specialist requirements.

## Academic and research basis
### Data validation and dependency contracts
- Breck, Zinkevich, Polyzotis, Whang & Roy, *Data Validation for Machine Learning* (SysML 2019): https://research.google/pubs/data-validation-for-machine-learning/
  - Supports treating input data quality, schema, and anomaly detection as first-class ML-system concerns rather than downstream cleanup.
- Sculley et al., *Hidden Technical Debt in Machine Learning Systems* (NeurIPS 2015): https://proceedings.neurips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf
  - Supports explicit management of data dependencies, consumers, changing external inputs, and system-level data assumptions.

### Leakage and dataset shift
- Kaufman, Rosset & Perlich, *Leakage in Data Mining: Formulation, Detection, and Avoidance* (KDD 2011), DOI 10.1145/2020408.2020496.
  - Supports the general rule that target-relevant information unavailable at legitimate decision time invalidates evaluation evidence.
- Quiñonero-Candela et al. (eds.), *Dataset Shift in Machine Learning* (MIT Press, 2008), DOI 10.7551/mitpress/9780262170055.001.0001.
  - Supports distinguishing real distribution change from simple data defects and evaluating train/test distribution differences explicitly.
### Missing data
- Rubin, *Inference and Missing Data* (Biometrika, 1976): https://www.ets.org/research/policy_research_reports/publications/article/1976/itce.html
- Moreno-Betancur et al., *Assumptions and analysis planning in studies with missing data in multiple variables: moving beyond the MCAR/MAR/MNAR classification* (International Journal of Epidemiology, 2023): https://academic.oup.com/ije/article/52/4/1268/7034967
  - Supports treating missingness mechanisms as substantive assumptions, not labels inferred from a null percentage, and motivates preserving richer missingness context for downstream analysis.

### Reproducibility, provenance, and dataset identity
- Sandve et al., *Ten Simple Rules for Reproducible Computational Research* (PLOS Computational Biology, 2013), DOI 10.1371/journal.pcbi.1003285.
  - Supports tracking how every result was produced, avoiding unrecorded manual manipulation, and preserving exact versions of external inputs and custom code.
- Wilkinson et al., *The FAIR Guiding Principles for scientific data management and stewardship* (Scientific Data, 2016), DOI 10.1038/sdata.2016.18.
  - Supports persistent identity, rich metadata, qualified references, provenance, interoperability, and reuse of data and workflows.
- González-Cebrián et al., *Standardised Versioning of Datasets: a FAIR-compliant Proposal* (Scientific Data, 2024): https://www.nature.com/articles/s41597-024-03153-y
  - Supports explicit dataset versioning and traceable comparison of dataset revisions.
- Gebru et al., *Datasheets for Datasets* (Communications of the ACM, 2021): https://www.microsoft.com/en-us/research/publication/datasheets-for-datasets/
  - Supports documenting dataset motivation, composition, collection process, recommended uses, and limitations for consumer transparency.

### Ordered forecasting evidence
- Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed., time-series cross-validation: https://otexts.com/fpp3/tscv.html
  - Supports evaluation designs in which each forecast is constructed only from observations available before its forecast origin. The repository generalizes the same anti-look-ahead principle to data availability/publication cutoffs.

## Repository-owned synthesis
The academic sources do not prescribe one universal file format, hash canonicalization, lakehouse architecture, missingness code set, or pipeline technology. Issue #134 therefore adopts principles rather than copying implementation recipes:

- make contracts and semantics explicit;
- preserve provenance and version identity;
- separate what happened from when it became knowable;
- avoid leakage across decision/evaluation boundaries;
- preserve missingness meaning where it changes interpretation;
- require independently checkable reconstruction evidence;
- use deterministic logical identity across equivalent serializations and byte identity only when exact serialization is controlled.

These are repository-owned adaptations derived from the evidence above and the harvested specialist family. If later evidence contradicts them, revise the adopted skill through the repository evaluation process rather than silently changing the source interpretation.
