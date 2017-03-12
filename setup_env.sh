#!/bin/bash

if [[ -z $1 ]]; then
  echo Usage: ./setup_env.sh path/to/your/homedir/repos
  exit
fi

# Activate virtualenv
. venv/bin/activate

# Set repo dir
export REPOS=${HOME}/$1
export PYTHONPATH_ORIG=${PYTHONPATH}
unset PYTHONPATH
export POLICY_DIFFUSION=$REPOS/policy_diffusion
export PYTHONPATH=${POLICY_DIFFUSION}/lid:${PYTHONPATH}
export PYTHONPATH=${POLICY_DIFFUSION}/lid/etl:${PYTHONPATH}
export PYTHONPATH=${POLICY_DIFFUSION}/lid/utils:${PYTHONPATH}
export PYTHONPATH=${POLICY_DIFFUSION}/lid/evaluation:${PYTHONPATH}
export PYTHONPATH=${POLICY_DIFFUSION}/scripts:${PYTHONPATH}:${PYTHONPATH_ORIG}

