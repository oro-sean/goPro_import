#!/bin/bash

echo "sleep for 30"

sleep 30

echo "setting conda"

source /home/camcontrol/anaconda3/etc/profile.d/conda.sh

echo "activate conda env"

conda activate goPro_import

echo "change working directory"

cd /home/camcontrol/goPro_import

echo "launch go_pro start"

python goPro_start.py
