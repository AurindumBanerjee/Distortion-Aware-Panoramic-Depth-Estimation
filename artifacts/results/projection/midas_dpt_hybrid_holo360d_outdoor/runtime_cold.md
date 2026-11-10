| method                                |   wall_s |   model_calls |   model_time_s |   post_time_s |   peak_gpu_mem_mb |   overhead_x |
|:--------------------------------------|---------:|--------------:|---------------:|--------------:|------------------:|-------------:|
| baseline                              |    3.585 |         1.000 |          3.576 |         0.001 |               nan |        1.000 |
| tangent|t45|v1|cosine|prior           |    9.552 |         3.000 |          9.025 |         0.494 |               nan |        2.665 |
| rotation|t45|pitch90_pm|cosine|prior  |   15.701 |         3.000 |         14.844 |         0.845 |               nan |        4.380 |
| hybrid|t45|v1|pitch90_pm|cosine|prior |   17.496 |         5.000 |         16.283 |         1.186 |               nan |        4.881 |