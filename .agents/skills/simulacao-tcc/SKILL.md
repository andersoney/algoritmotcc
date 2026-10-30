---
name: simulacao-tcc
description: Procedimentos de simulação de robótica móvel no Player/Stage (PCCEEV2) com suporte a robôs holonômicos e não-holonômicos, execução de batches e análise de métricas comparativas.
---

# Procedimentos de Simulação e Análise TCC

## 1. Execução de Simulações em Lote

### Parâmetros do `analise.sh`
O script recebe:
1. Quantidade de experimentos (`EXPERIMENTOS`, ex: `30` ou `40`).
2. Pasta de saída dos logs (`pasta_saida`, ex: `saida_v2` ou `saida_v2_holo`).
3. Modo holonômico (`holo_param`, use `holo` para ativar `drive "omni"` ou omita para diferencial).

Exemplo holonômico:
```bash
nohup taskset -c 3-15 bash analise.sh 30 saida_v2_holo holo &
```

Exemplo não-holonômico (diferencial):
```bash
nohup taskset -c 3-15 bash analise.sh 30 saida_v2 &
```

## 2. Geração de Gráficos e Métricas

O script `gerar_graficos_comparativos.py` gera gráficos a partir dos logs de simulação:

```bash
# Executar para a pasta de Logs padrão (/home/andersoney/workspace/Logs):
make graficos

# Executar para os logs gerados na pasta atual (.):
make graficos-local

# Executar manualmente com parâmetros:
./venv/bin/python gerar_graficos_comparativos.py -p pasta1 pasta2_holo -o ./meus_graficos
```

## 3. Estrutura dos Arquivos de Log (`logs_<exp>`)
- Linha 0: `num_robots`
- Linha 1: `numTotalIterations`
- Linha 2: `numMaxIterationsTotal` (ReachGoal + ExitGoal)
- Linha 3: `numMsgs`
- Linha 4: `numTotalIterationsReachGoal`
- Linha 5: `numTotalIterationsExitGoal`
- Linha 6: `numMaxIterationsReachGoal`
- Linha 7: `numMaxIterationsExitGoal`
- Linha 8: `numTotalStalls` (Colisões / Travamentos)
- Linha 9: `reachingTargetTime` (Tempo de simulação do Stage em $\mu\text{s}$)

