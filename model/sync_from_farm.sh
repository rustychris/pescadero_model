#!/bin/sh

VERSIONS="v114"

for V in $VERSIONS ; do
	echo $V
	rsync -rvPl --size-only -e 'ssh -p2022' --include '*/' --include '*0000.dia' --include '*0000_his.nc' --include '*.ini' --include '*.py' --include 'flowfm.mdu' --exclude '*' rustyh@farm.cse.ucdavis.edu:src/pescadero/model/model/run_salt_20160520-$V .
done

VERSIONS=""

# Map output:
for V in $VERSIONS ; do
	echo $V
	rsync -rvPl --size-only -e 'ssh -p2022' --include '*/' --include '*_map.nc' --exclude '*' rustyh@farm.cse.ucdavis.edu:src/pescadero/model/model/run_salt_20160520-$V .
done

