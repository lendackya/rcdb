#!/bin/bash


#Next lines just finds the path of the file
#Works for all versions,including
#when called via multple depth soft link,
#when script called by command "source" aka . (dot) operator.
#when arg $0 is modified from caller.
#"./script" "/full/path/to/script" "/some/path/../../another/path/script" "./some/folder/script"
#SCRIPT_PATH is given in full path, no matter how it is called.
#Just make sure you locate this at start of the script.
SCRIPT_PATH=$0:a:h;

#set our environment
export RCDB_HOME=$SCRIPT_PATH 
export LD_LIBRARY_PATH="$RCDB_HOME/lib":$LD_LIBRARY_PATH
export PYTHONPATH="$RCDB_HOME/python":$PYTHONPATH
export PATH="$RCDB_HOME":$PATH

