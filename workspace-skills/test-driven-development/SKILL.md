---
name: test-driven-development
description: Use when implementing a feature, bug fix, refactor, or behavior change where a test can define the intended behavior before production code is changed.
license: MIT
---

# Test-Driven Development

Use RED-GREEN-REFACTOR to prove a test can catch the missing behavior before the implementation exists.

## Iron law

For testable behavior changes, production code follows a meaningful failing test. A test written only after the implementation cannot demonstrate that it would have caught the missing behavior.

When repository authority documents a real exception—such as generated code, a throwaway spike, or behavior that cannot be exercised at the relevant layer—record the exception instead of pretending TDD occurred.

## RED

1. Write the smallest test for one required behavior.
2. Name the production change that should make this test pass.
3. Derive expected values from the requirement, not from the implementation under test.
4. Run the test and confirm it fails for the expected behavioral reason. Syntax errors, fixture errors, and unrelated failures are not RED.

Prefer real behavior over assertions about mocks or source text. Mock only boundaries that genuinely require isolation, after understanding the dependency's real side effects.## GREEN

1. Write only enough production code to satisfy the failing behavior.
2. Run the focused test and confirm it passes.
3. Run relevant surrounding tests so the local fix does not hide a regression.

## REFACTOR

Improve names, structure, duplication, and maintainability only while the tests remain green. Do not introduce new behavior during refactoring. Then repeat the cycle for the next behavior.

## When a failure is not understood

Use `systematic-debugging` before changing implementation. TDD defines intended behavior; it is not a substitute for root-cause analysis of an unexplained failure.

## Red flags and rationalizations

- "The code is too small to test." Small behavior still regresses.
- "I will add tests afterward." That is validation-after, not evidence that the test can detect absence of the feature.
- "I already tested it manually." Manual exploration does not create a repeatable regression guard.
- "Keeping the implementation as a reference is harmless." If the test is derived from existing code, it can become tautological.
- "The old code has no tests." The changed behavior still needs a reliable defining test where feasible.

## Boundaries

Repository test strategy, generated-code rules, safety policy, and explicit user constraints outrank this method. In KIS-managed repositories, KIS governs repository mutation and verification workflow; this skill owns only the RED-GREEN-REFACTOR method. Do not use the skill to authorize publication, external mutation, or skipped repository gates.