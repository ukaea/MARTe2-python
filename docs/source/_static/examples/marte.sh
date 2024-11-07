#!/bin/bash
#Arguments -f FILENAME -m MESSAGE | -s STATE [-d cgdb|strace]

MDS=0
DEBUG=""
INPUT_ARGS=$*
RESIDUALS=""
while test $# -gt 0
do
    case "$1" in
        -f|--file)
        CONFIG="$2"
        FQCONFIG=$(realpath "$(pwd)/$CONFIG")
        echo "config $1 $2"
        echo "fqconfig $1 $FQCONFIG"
        shift 2
        echo "args remaining $#"
        ;;
         -d|--debug)
        DEBUG="$2"
        echo "DEBUG $1 $2"
        shift 2
        echo "args remaining $#"
        ;;
        -mds)
        MDS=1
        echo "MDS: $1"
        shift
        echo "args remaining $#"
        ;;
        *)
        echo "Default: $1"
        RESIDUALS="$RESIDUALS $1"
        echo "RESIDUALS : $RESIDUALS"
        shift
        echo "args remaining $#"

        ;;
    esac
    #shift
done

echo "Parsed the input args, residuals are"
echo "$INPUT_ARGS"
echo "and dollar star is now $RESIDUALS"

if [ -z ${MARTe2_DIR+x} ]; then
export MARTe2_DIR=/root/MARTe2-dev
fi

if [ -z ${MARTe2_Components_DIR+x} ]; then
export MARTe2_Components_DIR=/root/MARTe2-components
fi

LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$MARTe2_DIR/Core/
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$MARTe2_Components_DIR/

#######################################
# Expand LD_LIBRARY_PATH for MARTe2_DIR
#######################################

m2_libs=$(find -L $MARTe2_DIR \
        -name '*.so' -printf '  %h\n' \
        -o -name '*.a' -printf ' %h\n' \
        -o -name '*.gam' -printf ' %h\n' \
        -o -name '*.drv' -printf ' %h\n' \
        | sort -u | \
        while read dir
        do
                printf ":%s" "$dir"
        done)

#echo "m2_libs is"
#echo "$m2_libs"
#exit 54
 
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}${m2_libs}

##################################################
# Expand LD_LIBRARY_PATH for MARTe2_Components_DIR
##################################################

m2_component_libs=$(find -L $MARTe2_Components_DIR \
        -name '*.so' -printf ' %h\n' \
        -name '*.a' -printf ' %h\n' \
        -name '*.gam' -printf ' %h\n' \
        -name '*.drv' -printf ' %h\n' \
        | sort -u | \
        while read dir
        do
                printf ":%s" "$dir"
        done)

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}${m2_component_libs}

#################################################
# Expand LD_LIBRARY_PATH for RunnerGAMs_DIR
#################################################
export LD_DEBUG=unused

if [ -z ${MARTe2_EXTRA_Components_DIR+x} ]; then
export MARTe2_EXTRA_Components_DIR=/root/Projects/marte2-extra-components
fi

runner_libs=$(find -L -L $MARTe2_EXTRA_Components_DIR \
        -name '*.so' -printf ' %h\n' \
        -name '*.a' -printf ' %h\n' \
        -name '*.gam' -printf ' %h\n' \
        -name '*.drv' -printf ' %h\n' \
        | sort -u | \
        while read dir
        do
                printf ":%s" "$dir"
        done)

LD_LIBRARY_PATH=${LD_LIBRARY_PATH}${runner_libs}
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$MARTe2_DIR/

echo "########################################################################################"
echo "# Dynamic Load Library Path for this invocation searches for components in directories #"
echo "########################################################################################"
tmpfile=$(mktemp /tmp/marte.XXXX)
echo $LD_LIBRARY_PATH| sed -e's/:/\n\t/g' > "$tmpfile"
mapfile -t LDLIBS < "$tmpfile"
echo "# Number of  directories : ${#LDLIBS[@]}                                               #"
cat "$tmpfile"
rm $tmpfile
echo "########################################################################################"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH

if [ ${MDS} == 1 ]; then
export rtappwriter_path=../Trees
export rtappreader_path=../Trees
export rtappdemo_path=../Trees
mdstcl < CreateMDSTrees.tcl
fi

if [ "$DEBUG" = "cgdb" ]
then
    taskset --cpu-list 1,2,3 cgdb --args $MARTe2_DIR/Build/x86-linux/App/MARTeApp.ex -f "$FQCONFIG" $RESIDUALS
elif [ "$DEBUG" = "gdb" ]
then 
    taskset --cpu-list 1,2,3 gdb --args $MARTe2_DIR/Build/x86-linux/App/MARTeApp.ex -f "$FQCONFIG" $RESIDUALS | tee gdb.log
elif [ "$TRACE" = "strace" ]
then 
    taskset --cpu-list 1,2,3  -f -o /tmp/strace.MARTeApp $MARTe2_DIR/Build/x86-linux/App/MARTeApp.ex  -f "$FQCONFIG" $RESIDUALS
else
    taskset --cpu-list 1,2,3 $MARTe2_DIR/Build/x86-linux/App/MARTeApp.ex -f "$FQCONFIG" $RESIDUALS 2>&1
fi
