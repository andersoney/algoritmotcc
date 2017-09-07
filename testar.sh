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
./createScenario automatic$2 $1 $2 $video        
if [ "$video" == "video" ]; then                 
  TIMEOUT=20000000m                              
else                                             
  TIMEOUT=10000m                                 
fi                                               
timeout $TIMEOUT stage $GUI automatic$2.world    