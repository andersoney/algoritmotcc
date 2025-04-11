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
for ((nRobos=20;nRobos<=500;nRobos+=20))
do
    #echo "*** determinar crescimento de RS em relacao $nRobos robos ****"
    for i in `seq 0 $((EXPERIMENTOS-1))`;
    do
        if [ ! -f "saidas/nRobos$nRobos/log\_$i" ]; then
            echo "$nRobos $i - Executando para $nRobos $i pois o arquivo saidas/nRobos$nRobos/log\_$i n existe"
            ./testar.sh $nRobos $i -gui &
        else
            echo "$nRobos $i - Não executando para $nRobos $i pois o arquivo saidas/nRobos$nRobos/log\_$i existe."
        fi
    done
done;
