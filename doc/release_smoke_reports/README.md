# Release Smoke Reports

Store completed release-candidate smoke-test reports in this directory.

For Apple-Silicon release verification, copy
`apple_silicon_smoke_test_template.md` to a release-specific file, for example:

```text
apple_silicon_smoke_test_2026.1-rc1.md
```

Each report should identify the exact DMG that was tested, its SHA-256, the
macOS host, the installed app path, runtime architecture checks, manual UI flow
results, and the final `pass`, `fail`, or `blocked` decision.

The canonical procedure is documented in
`doc/apple_silicon_build_smoke_test.md`.
