if [ $# -ge 1 ]; then
    EXPERIMENTOS=$1
else
    EXPERIMENTOS=40
fi


#make clean
make
max_concorrentes=30
for ((nRobos=20;nRobos<=500;nRobos+=20))
do
    for i in `seq 0 $((EXPERIMENTOS-1))`;
    do
        log_file="saidas/nRobots$nRobos/logs_$i"
        if [ -f "$log_file" ]; then
            echo "$nRobos $i - Log já existe, pulando..."
            continue
        fi
        
        while [ "$(jobs -rp | wc -l)" -ge "$max_concorrentes" ]; do
            sleep 1
        done
        
        mkdir -p "saidas/nRobots$nRobos"
        
        echo "$nRobos $i - Executando para $nRobos $i pois o arquivo saidas/nRobots$nRobos/log\_$i n existe"
        ./testar.sh $nRobos $i -gui &
        
    done
    echo "Todas as execuções finalizaram ${nRobos}"
done;
wait
echo "Todas as execuções finalizaram"
