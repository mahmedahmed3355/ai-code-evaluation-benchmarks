import ast, json
from pathlib import Path
# Independent static checks: candidate cannot simply delete the statistical boundaries.
root=Path('/app/ml_promo'); src=(root/'pipeline.py').read_text();
tree=ast.parse(src)
forbidden=['holdout']
assert 'assign_groups' in src and 'fit(X[tr])' in src and 'Zva=transform(X[va],state)' in src and 'Zho=transform(X[ho],state)' in src
assert 'min(cps,key=lambda c:(loss(y[va]' in src
assert 'fit_temperature(logits_v,y[va]' in src
assert 'cost_false_positive' in src and 'cost_false_negative' in src
assert 'split_fingerprint' in src and 'contract_version' in src
# Ensure verifier is not importing the candidate implementation.
vs=(Path('/app/tests/verify.py')).read_text(); assert 'from ml_promo' not in vs
print('INDEPENDENT PASS')
