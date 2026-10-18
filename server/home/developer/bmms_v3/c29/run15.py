import os,json,sys,statistics
from pathlib import Path
sys.path.insert(0,"/home/developer/bmms_v3/c26")
import measure_research as q
root=Path("/home/developer/bmms_v3/c29")
root.mkdir(exist_ok=True)
os.environ["AIC_METRIC"]="PipeUtilization"
specs=['1_1_1_32_1_0_0', '1_3_5_40_2_1_0', '2_7_13_48_1_0_1', '4_8_16_128_2_1_1', '8_16_32_128_1_0_0', '13_23_73_192_2_0_1', '16_32_128_256_1_1_0', '1_1025_1031_1032_2_1_1', '1_2048_1536_1280_1_0_1', '1_4096_1280_1152_2_0_0', '1_1536_2048_2048_1_1_1', '1_1280_4096_1536_2_1_0', '1_8192_64_128_1_0_0', '1_64_8192_128_2_0_1', '1_64_64_8192_1_1_1']
for variant in sys.argv[1:]:
 out=[]
 for i,spec in enumerate(specs,1):
  row=q.run_shape(variant,spec,"msprof",120,1,int(os.environ.get("BMMS_DEVICE_ID","0")))
  row["case"]=i
  if row.get("all_us"):row["warm_us"]=statistics.median(row["all_us"][-60:])
  out.append(row)
  (root/(variant+"_official15.json")).write_text(json.dumps(out,indent=2))
  print(json.dumps({k:row.get(k) for k in ["variant","case","warm_us","passed","tasks","error"]}),flush=True)
  if not row.get("passed"):sys.exit(2)
