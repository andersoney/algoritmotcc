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
 
export STAGEPATH=$PWD 
echo $STAGEPATH 
echo $video
shift 3
./createScenario worlds/automatic_${num_robot}_${exp} ${num_robot} ${exp} ${video} ${@}
echo "automatic_${num_robot}_${exp}.world"
# if [ "$video" == "video" ]; then  
#   TIMEOUT=20000000m
# else
#   TIMEOUT=10000m
# fi  
# timeout $TIMEOUT stage $GUI worlds/automatic_${num_robot}_${exp}.world 
echo "Startando stage"
stage $GUI worlds/automatic_${num_robot}_${exp}.world 