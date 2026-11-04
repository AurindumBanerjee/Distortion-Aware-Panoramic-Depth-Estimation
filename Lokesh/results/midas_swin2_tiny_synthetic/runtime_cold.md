| method                                |   wall_s |   model_calls |   model_time_s |   post_time_s |   peak_gpu_mem_mb |   overhead_x |
|:--------------------------------------|---------:|--------------:|---------------:|--------------:|------------------:|-------------:|
| baseline                              |    0.616 |         1.000 |          0.610 |         0.001 |               nan |        1.000 |
| tangent|t45|v1|cosine|prior           |    1.940 |         3.000 |          1.685 |         0.241 |               nan |        3.150 |
| rotation|t45|pitch90_pm|cosine|prior  |    2.249 |         3.000 |          1.829 |         0.415 |               nan |        3.651 |
| hybrid|t45|v1|pitch90_pm|cosine|prior |    3.564 |         5.000 |          2.880 |         0.672 |               nan |        5.786 |
| tangent|t45|v2|cosine|prior           |    3.214 |         5.000 |          2.655 |         0.425 |               nan |        5.218 |
| tangent|t45|v3|cosine|prior           |    4.502 |         7.000 |          3.670 |         0.804 |               nan |        7.309 |
| tangent|t45|v5|cosine|prior           |    6.956 |        11.000 |          5.849 |         1.069 |               nan |       11.292 |