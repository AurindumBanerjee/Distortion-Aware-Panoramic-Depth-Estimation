| method                                |   wall_s |   model_calls |   model_time_s |   post_time_s |   peak_gpu_mem_mb |   overhead_x |
|:--------------------------------------|---------:|--------------:|---------------:|--------------:|------------------:|-------------:|
| baseline                              |    5.559 |         1.000 |          5.553 |         0.001 |               nan |        1.000 |
| tangent|t45|v1|cosine|prior           |    9.058 |         3.000 |          8.808 |         0.237 |               nan |        1.629 |
| rotation|t45|pitch90_pm|cosine|prior  |   16.147 |         3.000 |         15.720 |         0.423 |               nan |        2.905 |
| hybrid|t45|v1|pitch90_pm|cosine|prior |   19.963 |         5.000 |         19.341 |         0.610 |               nan |        3.591 |
| tangent|t45|v2|cosine|prior           |   13.970 |         5.000 |         13.372 |         0.459 |               nan |        2.513 |
| tangent|t45|v3|cosine|prior           |   17.953 |         7.000 |         17.179 |         0.746 |               nan |        3.229 |
| tangent|t45|v5|cosine|prior           |   26.724 |        11.000 |         25.568 |         1.122 |               nan |        4.807 |