sed "s|\$ROBOCOMP|$ROBOCOMP|g" $ROBOCOMP/tools/rcnode/rcnode.conf > /tmp/rcnode.conf
icebox --Ice.Config=/tmp/rcnode.conf > /dev/null 2>&1