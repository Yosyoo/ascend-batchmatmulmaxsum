"""Offline round42b diagnostic and ABBA screen verification.

Run verify_quick.py for all four quick42_b layouts first; that checks every raw
duration and warm metric. This adds ordered case, shape, kernel and ratio checks.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).parent
EV = ROOT / 'evidence/remote_round28_round42_ab_screen20261015'
REMOTE = '/home/developer/bmms_v3/'
COL = json.loads((EV / 'collection_manifest.json').read_text())
FILES = {x['path']: x for x in COL['files']}
CHECKED = set()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def checked(path):
    key = path.relative_to(EV).as_posix()
    item = FILES[key]
    if key not in CHECKED:
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], key
        CHECKED.add(key)
    return path


def read(path):
    return json.loads(checked(path).read_text())


def identity(variant, hashes):
    source = checked(EV / f'variants/{variant}/kernel.asc')
    assert sha(source) == sha(ROOT / f'variants/{variant}/kernel.asc')
    for name, digest in hashes.items():
        key = f'variants/{variant}/' + (name if name == 'kernel.asc' else f'build/{name}')
        assert digest == COL['source_and_exe_sha256'][key]


precision = {}
precision_rows = {}
manifests = {}
for variant in ('s41c', 's42b'):
    folder = EV / f'solo17_data/diagnostic42_{variant}'
    summary = read(folder / 'summary.json')
    manifest = checked(folder / 'cases.txt')
    cases = manifest.read_text().splitlines()
    raw_log = checked(folder / 'precision.log')
    rows = [json.loads(line) for line in raw_log.read_text().splitlines() if line.startswith('{')]
    assert len(rows) == len(cases) == summary['observed'] == summary['expected'] == 656
    assert summary['passed'] is True and summary['failures'] == []
    assert sha(manifest) == summary['manifest_sha256']
    assert len(set(cases)) == len(cases)
    for i, (case, row) in enumerate(zip(cases, rows)):
        fields = case.split()
        nums = list(map(int, fields[:7]))
        assert row['case'] == i and row['shape'] == nums[:4]
        assert [row[k] for k in ('dtype', 'ta', 'tb')] == nums[4:]
        assert row['passed'] is True and row['consistent'] is True
        assert all(math.isfinite(row[k]) and row[k] >= 0 for k in ('absolute', 'relative'))
    identity(variant, summary['hashes'])
    precision[variant] = dict(manifest=rel(manifest), manifest_sha256=sha(manifest),
                              raw_log=rel(raw_log), expected=656, observed=656, passed=656,
                              failed=0, inconsistent=0, shape_dtype_layout_index_order_verified=True,
                              dtype_counts=dict(Counter(str(x['dtype']) for x in rows)),
                              layout_counts=dict(Counter(f"{x['ta']}{x['tb']}" for x in rows)))
    precision_rows[variant] = rows
    manifests[variant] = cases
assert manifests['s41c'] == manifests['s42b']
different_precision = [i for i, (a, b) in enumerate(zip(precision_rows['s41c'], precision_rows['s42b'])) if a != b]
new_fixture = checked(EV / 'solo17_data/a2_stress42.txt')
assert manifests['s42b'][496:] == new_fixture.read_text().splitlines()
prior_uncompleted = precision_rows['s42b'][592:]
assert len(prior_uncompleted) == 64 and all(x['passed'] and x['consistent'] for x in prior_uncompleted)

screens = []
total_tasks = 0
new_kernel_tasks = 0
shape_path = checked(EV / 'work/solo42/shapes_a.txt')
shapes = [list(map(int, line.split())) for line in shape_path.read_text().splitlines()]
assert len(shapes) == 5 and sha(shape_path) == sha(WORK / 'shapes_a.txt')
for layout in ('00', '01', '10', '11'):
    label = f'quick42_b_{layout}'
    folder = EV / f'solo17_data/{label}'
    comparison = read(folder / 'comparison.json')
    assert comparison['candidate'] == 's42b' and comparison['baseline'] == 's41c'
    assert comparison['dtype'] == 1 and [comparison['ta'], comparison['tb']] == list(map(int, layout))
    verification_path = WORK / f'pool_verified_s42b_{label}.json'
    verified = json.loads(verification_path.read_text())
    assert verified['raw_tasks_verified'] == 3200
    assert all(verified[k] for k in ('last80_medians_and_all_metrics_verified',
                                   'one_kernel_per_call_verified',
                                   'source_rehashed_and_recorded_exe_hashes_matched'))
    summaries = []
    profiles = []
    for order, variant in enumerate(('s41c', 's42b', 's42b', 's41c')):
        sub = folder / f'{order}_{variant}'
        summary = read(sub / 'summary.json')
        assert summary['order'] == order and summary['variant'] == variant
        assert summary['shape_sha256'] == sha(shape_path)
        assert [x['shape'] for x in summary['shapes']] == shapes
        assert [summary[k] for k in ('dtype', 'ta', 'tb')] == [1, *map(int, layout)]
        assert summary['tasks'] == 800 and summary['kernels_per_call'] == 1
        identity(variant, summary['hashes'])
        recorded_shapes = [list(map(int, line.split()[1:5]))
                           for line in checked(sub / 'msprof.log').read_text().splitlines()
                           if line.startswith('SHAPE ')]
        assert recorded_shapes == shapes
        profile = checked(EV / summary['profile'].removeprefix(REMOTE))
        with profile.open() as stream:
            raw = list(csv.DictReader(stream))
        operations = sorted([x for x in raw if 'bmms_' in x['Op Name']],
                            key=lambda x: float(x['Task Start Time(us)']))
        runtime = [x for x in raw if 'bmms_' not in x['Op Name']]
        assert all(x['Op Name'] == 'preload_stack_16KB' and int(x['Block Num']) == 0 for x in runtime)
        assert len(operations) == summary['tasks']
        for i, shape in enumerate(shapes):
            segment = operations[i*160:(i+1)*160]
            assert sorted({x['Op Name'] for x in segment}) == summary['shapes'][i]['op_names']
            assert len(segment) == 160
            if variant == 's42b':
                new_kernel_tasks += sum('bmms_pair_a2resident256' in x['Op Name'] for x in segment)
        total_tasks += len(operations)
        profiles.append(rel(profile))
        summaries.append(summary)
    per_shape = []
    for i, shape in enumerate(shapes):
        medians = [x['shapes'][i]['total_warm_us'] for x in summaries]
        ratios = [medians[1] / medians[0], medians[2] / medians[3]]
        for j, ratio in enumerate(ratios):
            recorded = comparison['orders'][j]['ratios'][i]
            assert recorded['shape'] == shape and recorded['ratio'] == ratio
        names = [x['shapes'][i]['op_names'] for x in summaries]
        assert names[1] == names[2] and names[0] == names[3]
        active = any('bmms_pair_a2resident256' in name for name in names[1])
        per_shape.append(dict(shape=shape, last80_us_abba=medians,
                              ratios_candidate_over_baseline=ratios,
                              geomean_ratio=math.sqrt(math.prod(ratios)),
                              candidate_kernel=names[1], baseline_kernel=names[0],
                              candidate_hits_new_kernel=active,
                              both_orders_faster=max(ratios) < 1))
    geomeans = [math.exp(statistics.mean(math.log(x['ratios_candidate_over_baseline'][i]) for x in per_shape))
                for i in (0, 1)]
    assert all(math.isclose(x, y, rel_tol=1e-14) for x, y in zip(geomeans, verified['ratios']))
    groups = {}
    for name, flag in [('new_kernel', True), ('retained_kernel', False)]:
        items = [x for x in per_shape if x['candidate_hits_new_kernel'] == flag]
        vals = [r for x in items for r in x['ratios_candidate_over_baseline']]
        groups[name] = dict(shapes=len(items), geometric_mean_ratio=math.exp(statistics.mean(map(math.log, vals))),
                           min_ratio=min(vals), max_ratio=max(vals),
                           all_shapes_both_orders_faster=all(x['both_orders_faster'] for x in items))
    screens.append(dict(label=label, dtype=1, layout=layout, baseline='s41c', candidate='s42b',
                         raw_tasks=3200, raw_profiles=profiles, raw_verification=rel(verification_path),
                         paired_order_geomean_ratios=geomeans,
                         combined_geomean_ratio=math.sqrt(math.prod(geomeans)),
                         by_kernel_path=groups, per_shape=per_shape))
assert total_tasks == 12800 and new_kernel_tasks == 2560

result = dict(round=42, variant='s42b', status='targeted_precision_and_four_layout_screen_verified',
              evidence_root=rel(EV), collection_manifest=rel(EV / 'collection_manifest.json'),
              collection_manifest_sha256=sha(EV / 'collection_manifest.json'),
              collection_listed_files=len(FILES), independently_rehashed_used_files=len(CHECKED),
              source_sha256=COL['source_and_exe_sha256']['variants/s42b/kernel.asc'],
              identity_scope='Source bytes locally rehashed against archive and collection; executable SHA-256 '
                             'records match summaries and collection, but executable bytes are not archived.',
              precision=precision,
              precision_comparison=dict(same_656_case_manifest=True,
                                        differing_logged_results=len(different_precision),
                                        differing_case_indices=different_precision,
                                        previously_uncompleted_42a_cases_now_passed_on_42b=64),
              screens=screens, raw_tasks_verified=total_tasks,
              candidate_new_kernel_raw_tasks=new_kernel_tasks,
              last80_medians_and_all_metrics_verified=True,
              one_kernel_per_call_task_count_verified=True,
              full_s42b_precision_suite_verified=False, full_100_shape_pool_verified=False,
              six_hang_regressions_verified=False, direct_s33a_comparison_verified=False,
              limits=[
                  'This archive establishes only s42b 656-case diagnostics and five FP16 shapes in four layouts against s41c.',
                  'Only shapes [1,2048,1024,256] and [4,512,1024,256] hit the new kernel in these screens; the other three retain bmms_pair_static.',
                  'The full s41c suites in the archive are baseline evidence and do not establish full s42b validation.',
                  'Separate s42b full validation, 100-shape pool, six hang regressions and direct s33a comparison were not part of these verified results.',
                  'Archived failure_a/state.json has stale unexecuted_remaining_cases=64 wording. Preserve archive: s42a actually has one runtime-failed case plus 63 subsequent unexecuted cases; see result_a.json.',
                  'Precision equality refers to logged errors and flags, not a bytewise comparison of saved operator outputs.',
              ])
(WORK / 'result_b_screen.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(result=rel(WORK / 'result_b_screen.json'), raw_tasks=total_tasks,
                      precision_passed=656, precision_log_differences=len(different_precision),
                      new_kernel_tasks=new_kernel_tasks,
                      layouts={x['layout']:dict(paired=x['paired_order_geomean_ratios'], paths=x['by_kernel_path']) for x in screens})))
