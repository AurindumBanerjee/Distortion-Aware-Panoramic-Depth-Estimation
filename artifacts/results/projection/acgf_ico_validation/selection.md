# acgf|ico validation selection (results/acgf_ico_validation)

Rule: configs/acgf_ico.yaml header (ties within 0.005 -> lower harm -> simpler).

## ico-grid (criterion: mean per-image polar AbsRel, align-equatorial)

| method                          |   criterion |   harm_% |   n_images |
|:--------------------------------|------------:|---------:|-----------:|
| acgf|ico-grid|polar|g43-87|s4   |      0.3317 |   9.7561 |         41 |
| acgf|ico-grid|polar|g43-87|s40  |      0.3246 |   9.7561 |         41 |
| acgf|ico-grid|polar|g43-87|s400 |      0.3184 |   7.3171 |         41 |
| acgf|ico-grid|polar|g43|s4      |      0.3285 |   9.7561 |         41 |
| acgf|ico-grid|polar|g43|s40     |      0.3233 |   7.3171 |         41 |
| acgf|ico-grid|polar|g43|s400    |      0.3183 |   7.3171 |         41 |

**chosen: acgf|ico-grid|polar|g43|s400** -> grids [[4, 3]], lam_smooth 400

## sphere_lambda (criterion: mean per-image whole-image AbsRel)

| method                       |   criterion |   harm_% |   n_images |
|:-----------------------------|------------:|---------:|-----------:|
| acgf|ico-affine|sphere|lam5  |      0.2549 |    4.878 |         41 |
| acgf|ico-affine|sphere|lam50 |      0.26   |    4.878 |         41 |

**chosen: acgf|ico-affine|sphere|lam5** -> sphere_lambda 5

## reference (not selected on): polar AbsRel

| method                |   criterion |   harm_% |   n_images |
|:----------------------|------------:|---------:|-----------:|
| acgf                  |      0.3243 |   9.7561 |         41 |
| mono360               |      0.1812 |   7.3171 |         41 |
| acgf|ico-affine|polar |      0.3077 |   7.3171 |         41 |
