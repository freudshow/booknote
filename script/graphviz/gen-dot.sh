#!/bin/bash

HMC="$1"

serverlist=`ssh -q -o "BatchMode yes" $HMC lssyscfg -r sys -F "name" | sort`

echo "graph hmc_graph{"

for server in $serverlist; do
    echo " \"$HMC\" -- \"$server\" "
    lparlist=`ssh -q -o "BatchMode yes" $HMC lssyscfg -m $server -r lpar -F "name" | sort`
    for lpar in $lparlist; do
             echo "    \"$server\" -- \"$lpar\" "
    done
done

echo "}"
