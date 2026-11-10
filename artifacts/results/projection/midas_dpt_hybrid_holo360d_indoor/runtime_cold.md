| method                                |   wall_s |   model_calls |   model_time_s |   post_time_s |   peak_gpu_mem_mb |   overhead_x |
|:--------------------------------------|---------:|--------------:|---------------:|--------------:|------------------:|-------------:|
| baseline                              |    7.319 |         1.000 |          7.300 |         0.004 |               nan |        1.000 |
| tangent|t45|v1|cosine|prior           |   15.119 |         3.000 |         14.299 |         0.769 |               nan |        2.066 |
| rotation|t45|pitch90_pm|cosine|prior  |   23.453 |         3.000 |         22.039 |         1.388 |               nan |        3.204 |
| hybrid|t45|v1|pitch90_pm|cosine|prior |   30.209 |         5.000 |         28.138 |         2.015 |               nan |        4.127 |