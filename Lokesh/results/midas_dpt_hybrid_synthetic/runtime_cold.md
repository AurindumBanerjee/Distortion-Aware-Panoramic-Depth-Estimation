| method                                |   wall_s |   model_calls |   model_time_s |   post_time_s |   peak_gpu_mem_mb |   overhead_x |
|:--------------------------------------|---------:|--------------:|---------------:|--------------:|------------------:|-------------:|
| baseline                              |    6.645 |         1.000 |          6.635 |         0.001 |               nan |        1.000 |
| tangent|t45|v1|cosine|prior           |   13.352 |         3.000 |         12.897 |         0.423 |               nan |        2.010 |
| rotation|t45|pitch90_pm|cosine|prior  |   20.159 |         3.000 |         19.364 |         0.783 |               nan |        3.034 |
| hybrid|t45|v1|pitch90_pm|cosine|prior |   27.444 |         5.000 |         26.266 |         1.149 |               nan |        4.130 |
| tangent|t45|v2|cosine|prior           |   21.003 |         5.000 |         19.912 |         0.847 |               nan |        3.161 |
| tangent|t45|v3|cosine|prior           |   25.497 |         7.000 |         24.276 |         1.179 |               nan |        3.837 |
| tangent|t45|v5|cosine|prior           |   38.563 |        11.000 |         36.519 |         1.977 |               nan |        5.804 |