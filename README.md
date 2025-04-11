#Algoritmo-TCC

##Como usar

Ultilize em sequencia os seguintes comandos:

    make
    testar.sh 50 0 gui
## Analise
 nohup taskset -c 17-31 bash analise.sh

## Matar o processo
pkill -f analise
pkill -f createScenario
pkill -f stage
