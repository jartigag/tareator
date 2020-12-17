#!/bin/bash
gawk -vFS=, -vOFS=, '{ $1 = mktime(gensub("[-:T]", " ", "g", $1)) } 1' $1
