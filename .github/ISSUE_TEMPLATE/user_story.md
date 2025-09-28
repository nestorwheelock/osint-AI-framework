---
name: User Story
about: Create a user story with AC and AI brief
title: "US-###: <title>"
labels: ["user-story"]
---

## Story
As a <role>, I want <capability>, so that <value>.

## Acceptance Criteria
- [ ] ...

## Test Plan
- pytest: ...
- Playwright: ...

## AI Coding Brief
```yaml
role: "You are a senior engineer practicing strict TDD."
objective: "Make the failing tests pass with the smallest change."
constraints:
  allowed_paths:
    - backend/app/**/*
tests_to_make_pass: []
definition_of_done:
  - "All referenced tests pass in CI"
```
