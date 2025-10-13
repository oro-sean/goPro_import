#!/bin/bash

echo "Launching goPro starter"

sleep 30

source /home/camcontrol/anaconda3/etc/profile.d/conda.sh

conda activate goPro_import

cd /home/camcontrol/goPro_import

python goPro_start.py


