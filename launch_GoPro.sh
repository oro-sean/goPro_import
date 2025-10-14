#!/bin/bash

echo "sleep for 30"

sleep 30

echo "here"

source /home/camcontrol/anaconda3/etc/profile.d/conda.sh

echo "here 2"

conda activate goPro_import

echo "here 3"

cd /home/camcontrol/goPro_import

echo "here 4"

python goPro_start.py
