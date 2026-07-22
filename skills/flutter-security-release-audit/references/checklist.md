# Flutter security and release checklist

## Secrets and configuration

- No production secrets, private keys, keystores, passwords, or embedded credentials in source/history/artifacts.
- Environment selection cannot silently ship staging endpoints or debug flags.
- Logs and crash reports redact tokens, personal data, and sensitive payloads.

## Authentication and storage

- Token lifetime, refresh, revocation, logout, and device restore behavior are defined.
- Sensitive values use platform-appropriate protected storage where the threat model requires it.
- Local databases/files define encryption, backup, export, and deletion behavior.
- Screenshots, clipboard, notifications, and app switcher exposure are considered for sensitive screens.

## Network and WebView

- Cleartext transport exceptions are scoped and justified.
- TLS/custom trust behavior does not bypass validation unintentionally.
- WebView navigation, JavaScript, file access, bridges, downloads, and external URL handling are restricted.
- Redirect/deep-link inputs are validated and cannot cross trust boundaries silently.

## Platform configuration

- Android exported components, intent filters, backup, permissions, FileProvider, and network security config.
- iOS URL schemes, associated domains, ATS exceptions, entitlements, background modes, and privacy manifests.
- Platform channels validate caller-controlled data and native errors.

## Dependencies and supply chain

- Lockfiles and toolchain versions are reproducible.
- Git/path dependencies, overrides, forks, abandoned plugins, and install scripts have owners.
- CI secrets have least privilege and are not exposed to untrusted pull requests.

## Release

- Debug/test code is excluded from production variants.
- Signing keys and store credentials are isolated and recoverable.
- Obfuscation/symbol files are retained for crash diagnosis.
- Versioning, migrations, rollout, monitoring, rollback, and emergency release procedures exist.
