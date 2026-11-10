| method                                |   wall_s |   model_calls |   model_time_s |   post_time_s |   peak_gpu_mem_mb |   overhead_x |
|:--------------------------------------|---------:|--------------:|---------------:|--------------:|------------------:|-------------:|
| baseline                              |    5.823 |         1.000 |          5.816 |         0.001 |               nan |        1.000 |
| tangent|t45|v1|cosine|prior           |   10.759 |         3.000 |         10.414 |         0.326 |               nan |        1.848 |
| rotation|t45|pitch90_pm|cosine|prior  |   16.902 |         3.000 |         16.336 |         0.558 |               nan |        2.903 |
| hybrid|t45|v1|pitch90_pm|cosine|prior |   20.411 |         5.000 |         19.599 |         0.794 |               nan |        3.505 |
| tangent|t45|v2|cosine|prior           |   14.807 |         5.000 |         14.001 |         0.647 |               nan |        2.543 |
| tangent|t45|v3|cosine|prior           |   21.956 |         7.000 |         20.817 |         1.099 |               nan |        3.771 |
| tangent|t45|v5|cosine|prior           |   31.089 |        11.000 |         29.662 |         1.354 |               nan |        5.339 |