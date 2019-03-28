#!/bin/bash

#get code
echo "getting code"
wget https://github.com/vgsatorras/few-shot-gnn/archive/master.zip
unzip master.zip
rm master.zip

#get data
echo "Getting data"
cd few-shot-gnn-master/
cd datasets/compressed/omniglot/
wget https://github.com/brendenlake/omniglot/raw/master/python/images_background.zip
wget https://github.com/brendenlake/omniglot/raw/master/python/images_evaluation.zip
cd ../../..

#setup env
echo "setting up conda environment"
conda ceate -n torch_env python=3
conda activate torch_env
conda install pytorch=0.4.1 torchvision cudatoolkit=10.0 -c pytorch

echo "Done."