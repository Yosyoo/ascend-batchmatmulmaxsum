# Ascend BatchMatmulMaxSum archive

Private source snapshot of the Ascend/CANN BatchMatmulMaxSum development work, archived on 2026-10-18 (Asia/Shanghai).

## Contents

- `server/home/developer/`: source, scripts, documentation, configuration, and text measurement records from **all six `bmms*` project directories** on the development server: `bmms_codex`, `bmms_codex_round2`, `bmms_final`, `bmms_fused`, `bmms_opt`, and `bmms_v3`.
- `final-delivery/`: the locally verified final `clean203` source and its official submission, performance, and review records.
- `historical-high-score/`: the retained `clean197` source and its historical score records.
- `metadata/server-manifest.json`: original server-relative paths, exact file sizes, SHA-256 digests, permissions, internal symlink relationships, scope, and exclusion counts.
- `embedded-archives/`: source and text records extracted from historical server archives; binary tensor datasets remain excluded. `metadata/embedded-manifest.json` records the original archive/member and the digest of every preserved file.
- `tools/`: the scripts used to create and verify this snapshot.

## Final submitted version

The final competition submission was **893147**, submitted at **2026-10-17 17:53:48 Asia/Shanghai**, before the 18:00 deadline.

- Variant: **clean203**
- Official result: **15/15 Pass**, **63.72 points**, **rank 29**
- Source SHA-256: `9feb4e97863b23d014f85f59393629ebb775b9b755dbd0262bd9847aa65c4a3e`
- Server source: `server/home/developer/bmms_v3/variants/clean203/kernel.asc`
- Verified local source: `final-delivery/kernel.asc`

The downloaded official source was compared byte-for-byte with the final source. Both copies are preserved here. Historical scores use different TBest references and should not be compared without normalization. The earlier 65.68-point `clean197` snapshot remains separately preserved.

Historical experiment folders include rejected, diagnostic, incomplete, and unsubmitted implementations. Their presence is an archival record, not a statement that every experiment passed correctness or compliance review. Final review records also document the known precision/validation limits.

## Scope and exclusions

This is a **project source archive**, not a full server disk image. It excludes SSH keys, credentials, shell history, IDE state, system/CANN installations, Git object databases, dependency environments, generated build/profiler trees, raw tensor datasets, binary outputs, and files exceeding the documented archive size threshold. Original server files were not modified or removed.

All selected regular files were checked for common credential patterns before upload. Every copied file is verified against the manifest. Internal project symlinks are normalized to relative links so the archived directory layout can be moved as a unit; external links are excluded. Some dataset links may point to raw data that is intentionally not part of a source archive.

The main server snapshot contains **9,150 regular files** and **5,113 internal symlink entries**. Historical compressed archives contribute **2,501 additional source/text entries**, including duplicate versions preserved in their original archive context. The main snapshot is approximately296MiB; the extracted historical entries are approximately109MiB before Git compression.

## Verification and restoration

Run from the repository root:

```sh
python3 tools/verify_archive.py
```

Restore the project source directories from `server/home/developer/` to a chosen development directory. Reinstall the required Ascend/CANN environment and regenerate raw test inputs as needed. The snapshot preserves existing project directory names and individual experimental versions; it does not reconstruct previous Git commit histories.

Keep this repository private. Existing notices and licenses in archived source directories continue to apply.
