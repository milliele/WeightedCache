#!/bin/sh

# Enable command echo
set -v

# Directory where this script is located
CURR_DIR=`pwd`

# Icarus main folder
ICARUS_DIR=${CURR_DIR}/../..

# Dir where plots will be saved 
PLOTS_DIR=${CURR_DIR}/plots

# Config file
CONFIG_FILE=${CURR_DIR}/config.py

# FIle where results will be saved
RESULTS_NAME=results-pd
RESULTS_FILE=${CURR_DIR}/${RESULTS_NAME}.pickle
RESULTS_TEXT=${CURR_DIR}/${RESULTS_NAME}.txt

# Add Icarus code to PYTHONPATH
export PYTHONPATH=${ICARUS_DIR}:$PYTHONPATH

# Plot results
echo "Plot results"
python ${CURR_DIR}/plotresults.py --results ${RESULTS_FILE} --output ${PLOTS_DIR} ${CONFIG_FILE}

### Read results
#echo "Read results"
#icarus results print ${RESULTS_FILE} > ${RESULTS_TEXT}