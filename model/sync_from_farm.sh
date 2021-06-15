#!/bin/sh

VERSIONS="v92 v93 v95 v93-restart"

for V in $VERSIONS ; do
	echo $V
	rsync -rvPl --size-only -e 'ssh -p2022' --include '*/' --include '*0000.dia' --include '*0000_his.nc' --include '*.py' --include 'flowfm.mdu' --exclude '*' rustyh@farm.cse.ucdavis.edu:src/pescadero/model/model/run_salt_20160520-$V .
done

VERSIONS="v93-restart"

# Map output:
for V in $VERSIONS ; do
	echo $V
	rsync -rvPl --size-only -e 'ssh -p2022' --include '*/' --include '*_map.nc' --exclude '*' rustyh@farm.cse.ucdavis.edu:src/pescadero/model/model/run_salt_20160520-$V .
done

