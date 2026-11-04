| method                                |   wall_s |   model_calls |   model_time_s |   post_time_s |   peak_gpu_mem_mb |   overhead_x |
|:--------------------------------------|---------:|--------------:|---------------:|--------------:|------------------:|-------------:|
| baseline                              |    6.093 |         1.000 |          6.089 |         0.001 |               nan |        1.000 |
| tangent|t45|v1|cosine|prior           |   10.851 |         3.000 |         10.571 |         0.265 |               nan |        1.781 |
| rotation|t45|pitch90_x2|cosine|prior  |   19.709 |         3.000 |         19.236 |         0.469 |               nan |        3.235 |
| hybrid|t45|v1|pitch90_x2|cosine|prior |   24.792 |         5.000 |         24.052 |         0.726 |               nan |        4.069 |
| tangent|t45|v2|cosine|prior           |   17.808 |         5.000 |         17.125 |         0.533 |               nan |        2.923 |
| tangent|t45|v3|cosine|prior           |   22.598 |         7.000 |         21.724 |         0.851 |               nan |        3.709 |
| tangent|t45|v5|cosine|prior           |   33.457 |        11.000 |         32.167 |         1.249 |               nan |        5.491 |