"""Mirror the verified preview to the root used by existing branch-based Pages.
Only files named by our generated manifest may be removed on subsequent builds.
"""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parent.parent;DIST=ROOT/'dist';manifest=ROOT/'.generated-files.json'
owned=json.loads(manifest.read_text()) if manifest.exists() else []
new={p.relative_to(DIST).as_posix() for p in DIST.rglob('*') if p.is_file()}
protected={'data','docs','tools','site','.github','.git'}
for name in owned:
 p=Path(name)
 if p.is_absolute() or '..' in p.parts or p.parts[0] in protected:raise ValueError('Unsafe generated manifest entry: '+name)
for name in set(owned)-new:
 p=ROOT/name
 if p.is_file():p.unlink()
for name in sorted(new):
 if Path(name).parts[0] in protected:raise ValueError('Build overlaps source: '+name)
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(DIST/name,p)
manifest.write_text(json.dumps(sorted(new),ensure_ascii=False,indent=2)+'\n')
print('Published root files:',len(new))
