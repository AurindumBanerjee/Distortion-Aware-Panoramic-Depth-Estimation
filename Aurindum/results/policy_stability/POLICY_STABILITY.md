# Policy stability: 40-frame vs 100-frame studies

Leave-one-dataset-out choice (headline rule) per model, held-out core set and fault.

| model | cells | same choice | different | 40-frame applies | 100-frame applies |
|---|---:|---:|---:|---:|---:|
| midas | 36 | 35 | 1 | 12 | 11 |
| dap | 36 | 35 | 1 | 20 | 20 |
| da360 | 36 | 33 | 3 | 6 | 7 |
| da2 | 36 | 34 | 2 | 14 | 14 |

## Cells where the choice differs

| model | held out | fault | 40 frames | 100 frames |
|---|---|---|---|---|
| midas | s3 | vfov | inpaint_tangent | none |
| dap | holo_in | vfov | inpaint_erp | plane_fill |
| da360 | panox | jpeg | bilateral | none |
| da360 | holo_in | tilt | none | relevel_known |
| da360 | holo_out | tilt | none | relevel_known |
| da2 | panox | yawblur | none | wiener |
| da2 | panox | jpeg | bilateral | none |
