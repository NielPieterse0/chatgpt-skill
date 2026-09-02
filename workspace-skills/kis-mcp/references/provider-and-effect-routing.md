# Provider and Effect Routing

Load this reference when a discovered operation's provider boundary, effect, or
execution surface is material to safe invocation.

## Determine the route from current evidence

Prefer the operation's runtime-reported `execution_surface` and effect metadata.
When that evidence is unavailable, use the durable classification:

- read-only effect -> read dispatcher;
- local filesystem/process/change effect -> change dispatcher;
- external provider effect -> external dispatcher.

A dispatcher is transport for the original operation contract. It does not grant
permission, weaken validation, authenticate a provider, satisfy approval, or
change repository authority.

## Resolve conflicts narrowly

If catalogue metadata, provider boundary, target repository authority, or the
live schema disagree, do not choose the broader interpretation. Report the
conflict and avoid the disputed action until current authority resolves it.

Do not infer external-provider authorization from:

- current working directory;
- a provider being registered, mounted, or ready;
- capability discovery or workflow recommendation;
- tool annotations or skill metadata.

Keep readiness, authentication, commissioning, authorization, and successful
execution as distinct evidence layers.

## Work policy interaction

The Work policy has exactly three hard rules, defined in `SKILL.md`. Provider
state, shell use, executable capabilities, uncertainty, or network-capable tools
do not create additional hard rules.

Evaluate the concrete effect. Local Work must not perform a proven external
network effect; approved external-provider operations belong on the external
provider surface instead.

Do not maintain provider names, versions, counts, current mounts, or current
commissioning status in this reference. Discover them from the running KIS
instance.