# Secret + Supply-Chain Scanner

Implement `/app/scanner.py`.

Invocation:

```bash
python /app/scanner.py --root /app/repo --config /app/repo/.scanignore.json --out /app/report.sarif
```

The scanner is defensive CI tooling. It must not contact external services.

## Output

Emit valid SARIF 2.1.0 with:
- one run;
- stable rule IDs;
- results sorted by `(artifact URI, line, column, ruleId)`;
- fingerprints stable across repeated runs;
- no secret value copied into SARIF.

Each result must include:
- `ruleId`
- `level`
- `message.text`
- `locations[0].physicalLocation.artifactLocation.uri`
- `region.startLine`
- `region.startColumn`
- `partialFingerprints.primaryLocationLineHash`

## Detection rules

### SECRET001 — AWS access key
Detect `AKIA`/`ASIA` followed by exactly 16 uppercase alphanumeric characters when used
as a credential-like token.

### SECRET002 — Private key
Detect PEM private-key begin markers.

### SECRET003 — GitHub token
Detect classic `ghp_` tokens and modern `github_pat_` tokens.

### SECRET004 — JWT
Detect three base64url segments separated by dots when the first segment decodes to a JWT
header containing `"alg"` and `"typ"`.

### SECRET005 — Generic credential assignment
Detect assignments such as:
`PASSWORD=`, `SECRET=`, `TOKEN=`, `API_KEY=`, `PRIVATE_KEY=`
when the value is non-empty, not a shell variable reference, and not an obvious placeholder.

### SECRET006 — High-entropy token
Detect a contiguous token of at least 24 characters containing upper/lower/digits and
symbol diversity, with Shannon entropy >= 4.0. Do not report ordinary UUIDs, hashes that
are explicitly named as checksums, or values on ignored lines.

### DEP001 — Unpinned container base
Detect `FROM image:tag` where tag is missing or `latest`, unless the line uses a digest
`@sha256:`.

### DEP002 — Floating Python dependency
Detect requirements lines with `package>=x`, `package`, or `package~=x` without an exact
`==` version. Ignore comments.

## Ignore configuration

`.scanignore.json`:

```json
{
  "paths": ["vendor/**", "fixtures/**"],
  "rules": ["DEP001"],
  "line_patterns": ["ALLOW_SECRET_SCANNER_TEST"]
}
```

Path globs are relative to root. Rule ignores suppress matching rules only.
Line patterns suppress findings on a line only.

Never let an ignore pattern suppress unrelated rules.

## File handling

- Scan UTF-8 text.
- Gracefully skip binary files and files that cannot be decoded.
- Do not follow symlinks outside root.
- Never scan `.git/`.
- URI paths must use `/` separators and be relative to root.
- Handle files larger than 2 MiB by streaming them line-by-line.

## Determinism / security

- Never print or write secret values.
- Do not use timestamps in the output.
- Do not include absolute filesystem paths.
- Identical input must produce byte-identical output.
- Do not hardcode the fixture.

Hidden tests include:
- near-miss AWS keys;
- fake examples in comments;
- secrets split across whitespace;
- Unicode;
- binary files;
- ignored subtrees;
- rule-specific ignores;
- high-entropy false positives;
- multiple findings on one line;
- CRLF;
- large files;
- reordered directory traversal.
