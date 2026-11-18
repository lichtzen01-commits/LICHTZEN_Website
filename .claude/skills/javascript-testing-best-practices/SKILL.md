---
name: javascript-testing-best-practices
description: Yoni Goldberg's JavaScript & Node.js testing best practices (50+ rules) — test anatomy (AAA, naming), black-box testing, realistic data, component/integration/E2E testing, mocking, flaky tests, frontend and backend testing, CI and test quality (coverage, mutation testing). Use when writing, reviewing or planning tests for JavaScript/TypeScript code, including the sales system engine and front-end scripts in this project.
---

# JavaScript testing best practices

Source: https://github.com/goldbergyoni/javascript-testing-best-practices (MIT, see LICENSE).

- `references/best-practices.md` — the full guide (English, ~2,200 lines). Grep for the section or rule you need; do not read it whole.
- `references/best-practices.ko.md` — Korean translation (may lag behind the English).

When writing or reviewing tests: name tests by what/when/expected, keep Arrange-Act-Assert, test behaviour not implementation, prefer realistic inputs, avoid shared mutable fixtures, and keep tests deterministic. Cite the rule title when giving review feedback.

## Sections

## 📗 50+ best practices: Super-comprehensive and exhaustive
## 🚢 Advanced: Goes 10,000 miles beyond the basics
## 🌐 Full-stack: front, backend, CI, anything
## `Table of Contents`
# Section 0️⃣: The Golden Rule
## ⚪️ 0 The Golden Rule: Design for lean testing
# Section 1: The Test Anatomy
## ⚪ ️ 1.1 Include 3 parts in each test name
## ⚪ ️ 1.2 Structure tests by the AAA pattern
## ⚪ ️1.3 Describe expectations in a product language: use BDD-style assertions
## ⚪ ️ 1.4 Stick to black-box testing: Test only public methods
## ⚪ ️ ️1.5 Choose the right test doubles: Avoid mocks in favor of stubs and spies
## 📗 Want to learn all these practices with live video?
## ⚪ ️1.6 Don’t “foo”, use realistic input data
## ⚪ ️ 1.7 Test many input combinations using Property-based testing
## ⚪ ️ 1.8 If needed, use only short & inline snapshots
## ⚪ ️ 1.9 Copy code, but only what's neccessary
## ⚪ ️ 1.10 Don’t catch errors, expect them
## ⚪ ️ 1.11 Tag your tests
## ⚪ ️ 1.12 Categorize tests under at least 2 levels
## ⚪ ️1.13 Other generic good testing hygiene
# Section 2️⃣: Backend Testing
## ⚪ ️2.1 Enrich your testing portfolio: Look beyond unit tests and the pyramid
## ⚪ ️2.2 Component testing might be your best affair
## ⚪ ️2.3 Ensure new releases don’t break the API using contract tests
## ⚪ ️ 2.4 Test your middlewares in isolation
## ⚪ ️2.5 Measure and refactor using static analysis tools
## ⚪ ️ 2.6 Check your readiness for Node-related chaos
## ⚪ ️2.7 Avoid global test fixtures and seeds, add data per-test
## ⚪ ️2.8 Choose a clear data clean-up strategy: After-all (recommended) or after-each
## ⚪ ️2.9 Isolate the component from the world using HTTP interceptor
## ⚪ ️2.10 Test the response schema, mostly when there are auto-generated fields
## ⚪ ️2.11 Check integrations corner cases and chaos
## ⚪ ️2.12 Test the five potential outcomes
# Section 3️⃣: Frontend Testing
## ⚪ ️ 3.1 Separate UI from functionality
## ⚪ ️ 3.2 Query HTML elements based on attributes that are unlikely to change
## ⚪ ️ 3.3 Whenever possible, test with a realistic and fully rendered component
## ⚪ ️ 3.4 Don't sleep, use frameworks built-in support for async events. Also try to speed things up
## ⚪ ️ 3.5 Watch how the content is served over the network
## ⚪ ️ 3.6 Stub flaky and slow resources like backend APIs
## ⚪ ️ 3.7 Have very few end-to-end tests that spans the whole system
## ⚪ ️ 3.8 Speed-up E2E tests by reusing login credentials
## ⚪ ️ 3.9 Have one E2E smoke test that just travels across the site map
## ⚪ ️ 3.10 Expose the tests as a live collaborative document
## ⚪ ️ 3.11 Detect visual issues with automated tools
# Section 4️⃣: Measuring Test Effectiveness
## ⚪ ️ 4.1 Get enough coverage for being confident, ~80% seems to be the lucky number
## ⚪ ️ 4.2 Inspect coverage reports to detect untested areas and other oddities
## ⚪ ️ 4.3 Measure logical coverage using mutation testing
## ⚪ ️4.4 Preventing test code issues with Test linters
# Section 5️⃣: CI and Other Quality Measures
## ⚪ ️ 5.1 Enrich your linters and abort builds that have linting issues
## ⚪ ️ 5.2 Shorten the feedback loop with local developer-CI
## ⚪ ️5.3 Perform e2e testing over a true production-mirror
## ⚪ ️5.4 Parallelize test execution
## ⚪ ️5.5 Stay away from legal issues using license and plagiarism check
## ⚪ ️5.6 Constantly inspect for vulnerable dependencies
## ⚪ ️5.7 Automate dependency updates
## ⚪ ️ 5.8 Other, non-Node related, CI tips
## ⚪ ️ 5.9 Build matrix: Run the same CI steps using multiple Node versions
## Yoni Goldberg
## [Bruno Scheufler](https://github.com/BrunoScheufler)
## [Ido Richter](https://github.com/idori)
## [Kyle Martin](https://github.com/js-kyle)
## Contributors ✨
