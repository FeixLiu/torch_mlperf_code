code from [mlperf v1.0 result](https://github.com/mlcommons/training_results_v1.0/tree/master/NVIDIA/benchmarks/bert/implementations/pytorch)

``` bash
cd 1_node_8_A100_PyTorch
```

### use these commands to compile mha relating op
```bash
cd ./mhalib
python setup.py build
cp build/lib*/mhalib* ../
cd ..
```

### run with this command
```bash
bash run_and_time.sh
```

### note
1. the data root path should be /workspace/bert_data
2. only update the extra params in `config_DGXA100_1x8x56x1.sh`, for other config file, follow the same `extra_params` in  `config_DGXA100_1x8x56x1.sh`
