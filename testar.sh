#!/bin/bash

num_robot="$1"
exp="$2"

if [ "$3" == "video" ]; then
  video="video" 
fi  
 
if [ "$video" != "video" ]; then  
  GUI="-g"
fi  
 
if [ "$3" == "gui" ]; then  
  GUI=""  
fi  
if [ -n "$4" ]; then
    var="$4"
else
    var="saidas"
fi
 
export STAGEPATH=$PWD 
echo $STAGEPATH 
echo $video
shift 3
mkdir -p ${var}/worlds
./createScenario ${var}/worlds/automatic_${num_robot}_${exp} ${num_robot} ${exp} ${video} ${@}
echo "automatic_${num_robot}_${exp}.world"
# if [ "$video" == "video" ]; then  
#   TIMEOUT=200000000000m
# else
#   TIMEOUT=1000000m
# fi  
# timeout $TIMEOUT stage $GUI worlds/automatic_${num_robot}_${exp}.world 
echo "Startando stage"
mkdir -p "${var}"
stage $GUI ${var}/worlds/automatic_${num_robot}_${exp}.world 
