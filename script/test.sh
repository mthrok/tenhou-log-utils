#!/bin/bash
set -eux -o pipefail
# Test command 
#
# Options
# --dir -d DIRECTORY
#     Directory where mjlog[.gz] files are found.

data_dir='./log'

while [ $# -gt 1 ]
do
    key="$1"
    value="$2"
    case $key in
	-d|--dir)
	    data_dir="${value}"
	    shift
	    ;;
	*)
	    echo "Unexpected option ${key}"
	    exit 1
	    ;;
    esac
    shift
done

for file in ${data_dir}/*.mjlog*
do
    tlu view "${file}"
done
