#!/bin/bash

PYTHON=python3

$PYTHON load.py test.xml

# output=$($PYTHON query.py '/child::a/child::b' | sort -g | paste -s -d' ' -)

# echo $output

# if [[ "$output" == "5 8 15" ]]; then
#     echo 'PASS'
# else
#     echo 'FAIL'
# fi

run_test() {
    query=$1 
    expected_output=$2

    output=$($PYTHON query.py "$1" | sort -g | paste -s -d' ' -)
    if [[ "$output" == "$expected_output" ]]; then
        echo 'PASS' $query 
    else
        echo 'FAIL' $query 
    fi
}

# simple step
run_test '/child::a' "1 7 13"

# joins
run_test '/child::a/child::b' "5 8 15"
run_test '/child::a/child::b/child::c'  "9"

# axes
run_test '/child::a/descendant::a' "3 10 14"
run_test '/child::a/descendant-or-self::a' "1 3 7 10 13 14"
run_test '/child::a/child::b/parent::a' "1 7 13"
run_test '/child::a/child::a/ancestor::a' "1 13"
run_test '/child::a/child::a/ancestor-or-self::a' "1 3 13 14"
run_test '/self::root' "0"
run_test '/child::a/self::a' "1 7 13"
run_test '/child::a/child::x/following-sibling::*' "3 4 5 6"
run_test '/child::a/child::y/following-sibling::*' "5 6"
run_test '/child::a/child::z/following-sibling::*' ""
run_test '/child::a/child::x/preceding-sibling::*' ""
run_test '/child::a/child::y/preceding-sibling::*' "2 3"
run_test '/child::a/child::z/preceding-sibling::*' "2 3 4 5"


# star node selection

run_test '/child::a/child::*' "2 3 4 5 6 8 14 15"

# filter expressions
run_test "/child::a[child::a]" "1 13"
run_test "/child::a[child::a and child::b]" "1 13"

