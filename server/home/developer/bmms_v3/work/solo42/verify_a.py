"""Offline verification of round42_a retrieved precision and failure evidence."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).parent
EV = ROOT / 'evidence/remote_round28_round42_a20261015'
REMOTE = '/home/developer/bmms_v3/'
COL = json.loads((EV / 'collection_manifest.json').read_text())
ENTRIES = {x['path']: x for x in COL['files']}
CHECKED = set()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def check(path):
    key = path.relative_to(EV).as_posix()
    item = ENTRIES[key]
    if key not in CHECKED:
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], key
        CHECKED.add(key)
    return path


def read(path):
    return json.loads(check(path).read_text())


def identity(variant, hashes):
    for name, digest in hashes.items():
        key = f'variants/{variant}/' + (name if name == 'kernel.asc' else 'build/' + name)
        assert digest == COL['source_and_exe_sha256'][key], (variant, name)
    source = check(EV / f'variants/{variant}/kernel.asc')
    assert sha(source) == sha(ROOT / f'variants/{variant}/kernel.asc')


def case_lines(path):
    data = check(path).read_text().splitlines()
    assert all(len(x.split()) == 8 for x in data), path
    return data


def inspect(manifest, log, expected, observed, passed):
    cases = case_lines(manifest)
    rows = [json.loads(x) for x in check(log).read_text().splitlines() if x.startswith('{')]
    assert len(cases) == expected and len(rows) == observed
    assert [x['case'] for x in rows] == list(range(observed))
    assert len(set(cases)) == expected
    for row, line in zip(rows, cases):
        nums = list(map(int, line.split()[:7]))
        assert row['shape'] == nums[:4]
        assert [row[x] for x in ('dtype', 'ta', 'tb')] == nums[4:]
        assert row['passed'] is True and row['consistent'] is True
        assert all(math.isfinite(row[k]) and row[k] >= 0 for k in ('absolute', 'relative'))
    assert passed == (observed == expected)
    return dict(manifest=relative(manifest), raw_log=relative(log), expected=expected,
                observed=observed, passed_records=observed, inconsistent=0,
                completed=observed == expected,
                shape_dtype_layout_index_order_verified=True), cases, rows


groups = {'historical': [], 'stress28': [], 'extra42': [], 'diagnostic42': []}
all_cases = {k: [] for k in groups}
all_rows = {k: [] for k in groups}


def add(group, name, item, cases, rows):
    groups[group].append(dict(suite=name, **item))
    all_cases[group].extend(cases)
    all_rows[group].extend(rows)


hist = read(EV / 'solo17_data/validation_s41c/precision_summary.json')
identity('s41c', hist['source_and_exe_sha256'])
assert hist['passed'] is True
for suite in hist['suites']:
    manifest = EV / suite['manifest'].removeprefix(REMOTE)
    log = EV / f"solo17_data/validation_s41c/{suite['suite']}.log"
    item, cases, rows = inspect(manifest, log, suite['expected'], suite['observed'], suite['passed'])
    assert max(x['absolute'] for x in rows) == suite['max_absolute']
    assert max(x['relative'] for x in rows) == suite['max_relative']
    add('historical', suite['suite'], item, cases, rows)
assert len(all_cases['historical']) == hist['total'] == 18378

stress = read(EV / 'solo17_data/stress28_s41c/summary.json')
identity('s41c', stress['hashes'])
assert stress['passed'] is True
for suite in stress['items']:
    name = suite['fixture']
    manifest = EV / f'solo17_data/{name}.txt'
    log = EV / f'solo17_data/stress28_s41c/{name}.log'
    item, cases, rows = inspect(manifest, log, suite['expected'], suite['observed'], suite['passed'])
    metadata = check(EV / f'solo17_data/{name}/fixture_hashes.json')
    assert sha(metadata) == suite['fixture_metadata_sha256']
    assert len(json.loads(metadata.read_text())) == len(rows)
    assert suite['returncode'] == 0 and suite['failures'] == []
    add('stress28', name, item, cases, rows)
assert len(all_cases['stress28']) == 672

for folder in sorted((EV / 'solo17_data').glob('extra42_*_s41c')):
    name = folder.name.removeprefix('extra42_').removesuffix('_s41c')
    suite = read(folder / 'summary.json')
    identity('s41c', suite['hashes'])
    manifest = EV / f'solo17_data/{name}.txt'
    item, cases, rows = inspect(manifest, folder / 'precision.log', suite['expected'], suite['observed'], suite['passed'])
    assert sha(manifest) == suite['manifest_sha256'] and suite['failures'] == []
    metadata = check(EV / f'solo17_data/{name}/fixture_hashes.json')
    assert sha(metadata) == suite['fixture_metadata_sha256']
    assert len(json.loads(metadata.read_text())) == len(rows)
    add('extra42', name, item, cases, rows)
assert len(all_cases['extra42']) == 2112

diags = {}
for variant, count in [('s41c', 656), ('s42a', 592)]:
    folder = EV / f'solo17_data/diagnostic42_{variant}'
    summary = read(folder / 'summary.json')
    identity(variant, summary['hashes'])
    item, cases, rows = inspect(folder / 'cases.txt', folder / 'precision.log',
                               summary['expected'], summary['observed'], summary['passed'])
    assert len(cases) == 656 and len(rows) == count
    assert sha(folder / 'cases.txt') == summary['manifest_sha256']
    assert sum(x['count'] for x in summary['origins']) == len(cases)
    assert summary['failures'] == []
    if variant == 's41c':
        add('diagnostic42', variant, item, cases, rows)
    diags[variant] = (item, cases, rows)
assert diags['s41c'][1] == diags['s42a'][1]
diag_cases = diags['s41c'][1]
assert case_lines(EV / 'solo17_data/a2_stress42.txt') == diag_cases[496:]

# Reconstruct the diagnostic selection from its historical source manifests;
# its two older appended manifests are supplied by the unchanged round41 packet.
old = ROOT / 'evidence/remote_round28_round41_acde20261015'
selected = []
origin_files = []
for origin in read(EV / 'solo17_data/diagnostic42_s41c/summary.json')['origins']:
    key = origin['path'].removeprefix(REMOTE)
    path = EV / key
    if path.is_file():
        check(path)
    else:
        path = old / key
        if not path.is_file():
            path = ROOT / 'evidence/remote_round18' / key
    assert path.is_file() and sha(path) == origin['sha256'], key
    subset = []
    for line in path.read_text().splitlines():
        b, m, n, k = map(int, line.split()[:4])
        if path.name in ('fail_8.txt', 'owned_stress41.txt', 'a2_stress42.txt') or (
                m >= 128 and n >= 128 and m % 128 == 0 and n % 128 == 0 and k >= 256 and k % 64 == 0):
            subset.append(line)
    assert len(subset) == origin['count']
    selected.extend(subset)
    origin_files.append(relative(path))
assert selected == diag_cases

sets = {k: set(v) for k, v in all_cases.items()}
overlap = []
names = list(sets)
for i, left in enumerate(names):
    for right in names[i + 1:]:
        overlap.append(dict(left=left, right=right, shared_cases=len(sets[left] & sets[right])))
combined = [x for rows in all_cases.values() for x in rows]
assert len(combined) == 21818 and len(set(combined)) == 21482
first_result = {}
repeat_differences = []
for group in groups:
    for line, row in zip(all_cases[group], all_rows[group]):
        metrics = {k: v for k, v in row.items() if k != 'case'}
        if line in first_result and first_result[line] != metrics:
            repeat_differences.append(line)
        first_result.setdefault(line, metrics)
candidate_differences = [i for i, (a, b) in enumerate(zip(diags['s41c'][2], diags['s42a'][2]))
                         if {k:v for k,v in a.items() if k != 'case'} != {k:v for k,v in b.items() if k != 'case'}]

failure = read(EV / 'work/solo42/failure_a/state.json')
driver_path = check(EV / 'work/solo42/failure_a/debug_plog.log')
driver = driver_path.read_text().splitlines()
raw_error = check(EV / 'solo17_data/diagnostic42_s42a/precision.log').read_text()
assert 'ACL failure line 47 code 507015' in raw_error
assert failure['completed_cases'] == 592 and failure['expected_cases'] == 656
assert failure['acl_error'] == 507015 and failure['performance_ran'] is False
assert not list((EV / 'solo17_data').glob('quick42_a*'))
matches = {label: [i + 1 for i, text in enumerate(driver) if token in text]
           for label, token in [('L0B_conflict', 'L0B read/write conflict'),
                                ('runtime_507015', '507015'),
                                ('failed_kernel', 'bmms_pair_a2resident256'),
                                ('hardware_error', '0x8000004000')]}
assert all(matches.values())
first_missing = diag_cases[592].split()
assert list(map(int, first_missing[:4])) == failure['shape']
assert first_missing[-1].removeprefix(REMOTE) == failure['fixture']

result = dict(
    round=42, evidence_root=relative(EV),
    collection_manifest=relative(EV / 'collection_manifest.json'),
    collection_manifest_sha256=sha(EV / 'collection_manifest.json'),
    collection_files=len(ENTRIES), independently_rehashed_used_files=len(CHECKED),
    source_and_executable_identity=COL['source_and_exe_sha256'],
    identity_scope='Local and archived kernel bytes match. Executable hashes match run summaries and '
                   'collection records; executable bytes are not included and cannot be rehashed locally.',
    s41c=dict(suites=groups, group_observed={k:len(v) for k,v in all_cases.items()},
               all_logged_records_passed_and_consistent=True,
               pass_observations=21818, distinct_manifest_cases=21482,
               repeated_observations=336, overlaps=overlap,
               repeated_case_differing_error_metrics=len(repeat_differences),
               diagnostic_manifest_reconstructed=True, diagnostic_origin_files=origin_files),
    s42a=dict(**diags['s42a'][0], status='runtime_failure_before_performance',
              numeric_failure_rows=0, uncompleted_cases=64,
              first_uncompleted_case=592, first_uncompleted_shape=list(map(int, first_missing[:4])),
              first_uncompleted_dtype=int(first_missing[4]), first_uncompleted_layout=first_missing[5:7],
              first_uncompleted_fixture=first_missing[-1],
              first_uncompleted_case_attempted_but_no_precision_result=True,
              subsequent_unobserved_cases=63, full_precision_passed=False,
              runtime_error=507015, hardware_error='0x8000004000',
              driver_error='L0B read/write conflict in the MTE (same address)',
              driver_log=relative(driver_path), driver_evidence_lines=matches,
              completed_cases_differing_error_metrics_vs_s41c=len(candidate_differences),
              differing_metric_case_indices=candidate_differences,
              performance_ran=False, full_100_shape_pool_run=False),
    limits=[
        'Distinct cases are deduplicated by the full manifest row, including fixture path; this is not a binary-content deduplication.',
        '21,818 is a count of s41c passed observations, not independent fixtures; 336 diagnostic observations repeat historical cases.',
        'Archived fixture metadata and remote unchanged flags do not substitute for rehashing absent fixture binaries.',
        's42a has 592 passed records and 64 cases without a completed precision result; an empty numeric failures list does not mean the suite passed.',
        'The raw driver establishes L0B read/write conflict. The TPipe initial-event-token mechanism is a separate code diagnosis, not proved by this log alone.',
        'This verification performs no compilation, NPU execution, performance measurement or official submission.',
    ],
)
(WORK / 'result_a.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(result=relative(WORK / 'result_a.json'), groups=result['s41c']['group_observed'],
                      total_pass_observations=21818, unique_manifest_cases=21482,
                      repeated_differing_metrics=len(repeat_differences),
                      candidate_completed=592, candidate_uncompleted=64,
                      candidate_differing_metrics=len(candidate_differences),
                      driver=matches)))
