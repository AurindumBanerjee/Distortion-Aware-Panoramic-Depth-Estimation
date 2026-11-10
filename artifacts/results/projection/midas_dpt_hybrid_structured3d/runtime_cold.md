| method                                |   wall_s |   model_calls |   model_time_s |   post_time_s |   peak_gpu_mem_mb |   overhead_x |
|:--------------------------------------|---------:|--------------:|---------------:|--------------:|------------------:|-------------:|
| baseline                              |    4.342 |         1.000 |          4.330 |         0.003 |               nan |        1.000 |
| tangent|t45|v1|cosine|prior           |    9.258 |         3.000 |          8.786 |         0.443 |               nan |        2.132 |
| rotation|t45|pitch90_pm|cosine|prior  |   13.515 |         3.000 |         12.782 |         0.721 |               nan |        3.113 |
| hybrid|t45|v1|pitch90_pm|cosine|prior |   18.147 |         5.000 |         17.028 |         1.092 |               nan |        4.180 |