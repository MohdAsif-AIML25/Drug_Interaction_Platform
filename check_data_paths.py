from pathlib import Path
import os

os.chdir(r'C:\Users\91939\OneDrive\Desktop\drug-interaction-platform')
base_dir = Path('backend').resolve()
candidate_dirs = [base_dir / 'data', base_dir.parent / 'data', Path.cwd() / 'data']
print('BASE_DIR', base_dir)
files = ['eval copy.csv', 'test copy.csv', 'eval.csv', 'test.csv']
for p in candidate_dirs:
    print('CHECK', p, 'exists=', p.exists())
    for f in files:
        print('  ', f, (p / f).exists(), p / f)
