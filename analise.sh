MAXVEZES=3; #depois de criado, se o arquivo de log estava vazio faz de novo o experimento no máximo MAX_VEZES
ro=1;
# Argumento 1 é opcional e indica a quantidade de vezes que o experimento será rodado
if [ $# -ge 1 ]; then
  EXPERIMENTOS=$1
else
  EXPERIMENTOS=40
fi


#make clean
make

#determinar crescimento de t em relacao ao numero de robos
for ((nRobos=20;nRobos<=140;nRobos+=20))
do
  #echo "*** determinar crescimento de RS em relacao $nRobos robos ****"
  for i in `seq 0 $((EXPERIMENTOS-1))`; 
  do
    if [ ! -e nRobos$nRobos/log\_$i ]; then      
      echo "******* testar.sh $nRobos $logName ********" 
      bash ./testar.sh $nRobos $ro
      if [ ! -d nRobos$nRobos ]; then
        mkdir nRobos$nRobos;
      fi
      let vA=$i+1
      echo ""
      echo ""
      echo "*** determinar crescimento de RS em relacao $nRobos robos ****"
      echo ""
      echo ""
      echo "Experimento numero $vA"
      echo ""
      echo ""
      mv logs nRobos$nRobos/log\_$i;
      #mv $logName nRobos$nRobos/log\_$i;

      #depois de criado, se o arquivo estava vazio faz de novo no máximo MAX_VEZES
      vezes=0;
      while [ $vezes -lt $MAXVEZES ] && ( [ ! -s nRobos$nRobos/log\_$i  ] ||  grep -q 10000 nRobos$nRobos/log\_$i ) ; do
        echo "*** Rodando de novo, arquivo de log vazio ***" &>> logTestar$1
        bash ./testar.sh $nRobos $ro
        #mv $logName nRobos$nRobos/log\_$i;
        mv logs nRobos$nRobos/log\_$i;
        vezes=$((vezes+1));
      done;
    fi;
  done
done; 
