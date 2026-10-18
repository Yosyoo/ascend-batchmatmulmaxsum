from pathlib import Path
p=Path("harness/measure.py").read_text().replace("R = Path(__file__).resolve().parent", "R = Path(\"/home/developer/bmms_v3/harness\")")
p=p.replace("work = vd / 'work' / spec", "work = vd / 'research' / os.environ.get('AIC_METRIC','Memory') / spec")
p=p.replace("'--aic-metrics=PipeUtilization'", "'--aic-metrics=' + os.environ.get('AIC_METRIC','Memory')")
Path("c26/measure_research.py").write_text(p)
