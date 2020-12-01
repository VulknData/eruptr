#!/bin/bash

deactivate
conda deactivate
source ~/code/eruptr-venv/bin/activate
export PYTHONPATH="../:$PYTHONPATH"
