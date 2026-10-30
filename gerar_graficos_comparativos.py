#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script flexível e automatizado para geração de gráficos comparativos entre
diferentes algoritmos e suas variações (Holonômico vs Não Holonômico).

Funcionalidades:
  1. Varredura e descoberta automática de diretórios de logs (ex: em /home/andersoney/workspace/Logs ou locais).
  2. Identificação automática ou configurável de quais logs são holonômicos e não-holonômicos.
  3. Geração de gráficos:
     - Comparação interna (Holo vs Não-Holo) para cada algoritmo individual.
     - Comparação global entre todos os algoritmos Holonômicos.
     - Comparação global entre todos os algoritmos Não-Holonômicos.
     - Comparação geral combinada com todos os experimentos.
  4. Suporta tanto linha de comando (CLI) flexível quanto execução direta.
"""

import os
import sys
import argparse
import glob
from pathlib import Path
import math

try:
    import numpy as np
except ImportError:
    # Fallback caso numpy não esteja instalado
    class SimpleNP:
        @staticmethod
        def mean(lista):
            return sum(lista) / len(lista) if lista else 0.0
        
        @staticmethod
        def std(lista):
            if not lista or len(lista) <= 1:
                return 0.0
            m = sum(lista) / len(lista)
            var = sum((x - m) ** 2 for x in lista) / len(lista)
            return math.sqrt(var)
    np = SimpleNP()

# Configura backend headless para ambientes de servidor sem display
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# Paleta e marcadores consistentes para gráficos elegantes
CORES = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]
MARCADORES = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']


def ler_logs(pasta_base):
    """
    Lê todos os arquivos de log de uma pasta e retorna um dicionário
    com as métricas agrupadas por número de robôs.
    
    Formato esperado de cada arquivo 'logs_X':
      Linha 0: num_robots
      Linha 1: numTotalIterations
      Linha 2: numMaxIterationsTotal (numMaxIterationsReachGoal + numMaxIterationsExitGoal)
      Linha 3: numMsgs
      Linha 4: numTotalIterationsReachGoal
      Linha 5: numTotalIterationsExitGoal
      Linha 6: numMaxIterationsReachGoal
      Linha 7: numMaxIterationsExitGoal
      Linha 8: numTotalStalls
      Linha 9: reachingTargetTime (em microssegundos da simulação Stage)
    """
    dados = {}
    pasta_path = Path(pasta_base)
    
    if not pasta_path.exists():
        print(f"⚠️ Diretório não encontrado: {pasta_base}")
        return dados

    # Procura subpastas nRobots<N>
    for pasta_robot in sorted(pasta_path.glob("nRobots*")):
        if not pasta_robot.is_dir():
            continue
        
        try:
            num_robots = int(pasta_robot.name.replace('nRobots', ''))
        except ValueError:
            continue
        
        dados[num_robots] = {
            'numTotalStalls': [],
            'reachingTargetTime': [],
            'numMaxIterationsTotal': [],
            'numMsgs': []
        }
        
        # Lê arquivos logs_<exp>
        for arq in sorted(pasta_robot.glob("logs_*")):
            if arq.is_file():
                try:
                    with open(arq, 'r', encoding='utf-8') as f:
                        linhas = [l.strip() for l in f if l.strip()]
                    
                    if len(linhas) >= 10:
                        iter_tot = int(linhas[2])
                        msgs = int(linhas[3])
                        stalls = int(linhas[8])
                        # reachingTargetTime vem em microssegundos (us) do Stage -> converte para segundos
                        time_s = float(linhas[9]) / 1e6
                        
                        dados[num_robots]['numMaxIterationsTotal'].append(iter_tot)
                        dados[num_robots]['numMsgs'].append(msgs)
                        dados[num_robots]['numTotalStalls'].append(stalls)
                        dados[num_robots]['reachingTargetTime'].append(time_s)
                except Exception as e:
                    pass

    return dados


def calcular_estatisticas(dados):
    """
    Calcula média e desvio padrão para cada métrica ordenada por número de robôs.
    """
    stats = {
        'num_robots': [],
        'stalls_mean': [], 'stalls_std': [],
        'time_mean': [], 'time_std': [],
        'iterations_mean': [], 'iterations_std': [],
        'msgs_mean': [], 'msgs_std': []
    }
    
    for n in sorted(dados.keys()):
        # Ignora se não houver registros
        if len(dados[n]['reachingTargetTime']) == 0:
            continue
            
        stats['num_robots'].append(n)
        
        stalls = dados[n]['numTotalStalls']
        times = dados[n]['reachingTargetTime']
        iters = dados[n]['numMaxIterationsTotal']
        msgs = dados[n]['numMsgs']
        
        stats['stalls_mean'].append(np.mean(stalls))
        stats['stalls_std'].append(np.std(stalls))
        
        stats['time_mean'].append(np.mean(times))
        stats['time_std'].append(np.std(times))
        
        stats['iterations_mean'].append(np.mean(iters))
        stats['iterations_std'].append(np.std(iters))
        
        stats['msgs_mean'].append(np.mean(msgs))
        stats['msgs_std'].append(np.std(msgs))
        
    return stats


def plotar_comparacao_multipla(series_dict, titulo_sufixo, pasta_saida, prefixo_arquivo=''):
    """
    Gera gráficos comparativos contendo múltiplas séries.
    series_dict = {
        'Nome da Série': stats_dict,
        ...
    }
    """
    if not series_dict:
        return
        
    if plt is None:
        print("❌ 'matplotlib' não está instalado. Instale com: pip install matplotlib")
        return
        
    os.makedirs(pasta_saida, exist_ok=True)
    
    # 1. Total de Stalls
    plt.figure(figsize=(10, 6))
    for i, (nome, s) in enumerate(series_dict.items()):
        cor = CORES[i % len(CORES)]
        marcador = MARCADORES[i % len(MARCADORES)]
        plt.errorbar(s['num_robots'], s['stalls_mean'], yerr=s['stalls_std'],
                     label=nome, color=cor, marker=marcador, capsize=3, linewidth=2)
    plt.xlabel('Número de Robôs', fontsize=12)
    plt.ylabel('Total de Colisões/Stalls (média)', fontsize=12)
    plt.title(f'Comparação: Número de Robôs vs Total de Stalls ({titulo_sufixo})', fontsize=13, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}stalls.png'), dpi=200)
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}stalls.pdf'))
    plt.close()

    # 2. Tempo de Simulação (segundos)
    plt.figure(figsize=(10, 6))
    for i, (nome, s) in enumerate(series_dict.items()):
        cor = CORES[i % len(CORES)]
        marcador = MARCADORES[i % len(MARCADORES)]
        plt.errorbar(s['num_robots'], s['time_mean'], yerr=s['time_std'],
                     label=nome, color=cor, marker=marcador, capsize=3, linewidth=2)
    plt.xlabel('Número de Robôs', fontsize=12)
    plt.ylabel('Tempo de Simulação (s)', fontsize=12)
    plt.title(f'Comparação: Número de Robôs vs Tempo de Simulação ({titulo_sufixo})', fontsize=13, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}tempo_simulacao.png'), dpi=200)
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}tempo_simulacao.pdf'))
    plt.close()

    # 3. Iterações Máximas
    plt.figure(figsize=(10, 6))
    for i, (nome, s) in enumerate(series_dict.items()):
        cor = CORES[i % len(CORES)]
        marcador = MARCADORES[i % len(MARCADORES)]
        plt.errorbar(s['num_robots'], s['iterations_mean'], yerr=s['iterations_std'],
                     label=nome, color=cor, marker=marcador, capsize=3, linewidth=2)
    plt.xlabel('Número de Robôs', fontsize=12)
    plt.ylabel('Máximo de Iterações (ReachGoal + ExitGoal)', fontsize=12)
    plt.title(f'Comparação: Número de Robôs vs Máx. Iterações ({titulo_sufixo})', fontsize=13, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}iteracoes.png'), dpi=200)
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}iteracoes.pdf'))
    plt.close()

    # 4. Painel Combinado (3 subplots horizontais)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Subplot 1: Stalls
    for i, (nome, s) in enumerate(series_dict.items()):
        cor = CORES[i % len(CORES)]
        marcador = MARCADORES[i % len(MARCADORES)]
        axes[0].errorbar(s['num_robots'], s['stalls_mean'], yerr=s['stalls_std'],
                         label=nome, color=cor, marker=marcador, capsize=2, linewidth=1.8)
    axes[0].set_xlabel('Número de Robôs', fontsize=11)
    axes[0].set_ylabel('Total de Stalls', fontsize=11)
    axes[0].set_title('Total de Stalls', fontsize=12, fontweight='bold')
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)

    # Subplot 2: Tempo
    for i, (nome, s) in enumerate(series_dict.items()):
        cor = CORES[i % len(CORES)]
        marcador = MARCADORES[i % len(MARCADORES)]
        axes[1].errorbar(s['num_robots'], s['time_mean'], yerr=s['time_std'],
                         label=nome, color=cor, marker=marcador, capsize=2, linewidth=1.8)
    axes[1].set_xlabel('Número de Robôs', fontsize=11)
    axes[1].set_ylabel('Tempo de Simulação (s)', fontsize=11)
    axes[1].set_title('Tempo para Conclusão (s)', fontsize=12, fontweight='bold')
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)

    # Subplot 3: Iterações
    for i, (nome, s) in enumerate(series_dict.items()):
        cor = CORES[i % len(CORES)]
        marcador = MARCADORES[i % len(MARCADORES)]
        axes[2].errorbar(s['num_robots'], s['iterations_mean'], yerr=s['iterations_std'],
                         label=nome, color=cor, marker=marcador, capsize=2, linewidth=1.8)
    axes[2].set_xlabel('Número de Robôs', fontsize=11)
    axes[2].set_ylabel('Máx. Iterações', fontsize=11)
    axes[2].set_title('Iterações Máximas', fontsize=12, fontweight='bold')
    axes[2].legend(fontsize=9)
    axes[2].grid(True, alpha=0.3)

    plt.suptitle(f'Visão Geral Consolidada ({titulo_sufixo})', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}painel_combinado.png'), dpi=200, bbox_inches='tight')
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}painel_combinado.pdf'), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráficos salvos em: {pasta_saida} (prefixo: '{prefixo_arquivo}')")


def descobrir_diretorios(diretorio_raiz):
    """
    Percorre a árvore de pastas e detecta diretórios que contenham pastas nRobots*.
    Retorna uma lista de tuplas (nome_identificador, caminho_absoluto, is_holo).
    """
    raiz = Path(diretorio_raiz).resolve()
    candidatos = []
    
    # Se a própria raiz contém nRobots*, adiciona
    if any(p.is_dir() and p.name.startswith("nRobots") for p in raiz.iterdir() if p.is_dir()):
        candidatos.append(raiz)
    
    # Procura recursivamente em subdiretórios
    for p in sorted(raiz.glob("**/nRobots*")):
        pai = p.parent
        if pai not in candidatos:
            candidatos.append(pai)
            
    resultados = []
    for c in candidatos:
        # Nome relativo amigável
        try:
            rel = c.relative_to(raiz)
            nome = str(rel) if str(rel) != "." else c.name
        except ValueError:
            nome = c.name
            
        # Determina se é holonômico baseado no nome
        nome_lower = str(c).lower()
        is_holo = any(token in nome_lower for token in ['holo', 'omni'])
        
        resultados.append({
            'nome': nome,
            'caminho': str(c),
            'is_holo': is_holo
        })
        
    return resultados


def processar_experimentos(diretorios_info, pasta_saida_base):
    """
    Carrega dados de todos os diretórios identificados e gera comparações:
    1. Holo vs Não-Holo para o mesmo algoritmo (quando houver par).
    2. Comparação geral entre todos os Não-Holonômicos.
    3. Comparação geral entre todos os Holonômicos.
    4. Comparação global contendo todos os dados.
    """
    dados_carregados = {}
    stats_carregadas = {}
    
    print("\n📂 Carregando dados dos experimentos...")
    for item in diretorios_info:
        nome = item['nome']
        caminho = item['caminho']
        d = ler_logs(caminho)
        s = calcular_estatisticas(d)
        
        if len(s['num_robots']) > 0:
            dados_carregados[nome] = item
            stats_carregadas[nome] = s
            status_holo = "Holonômico" if item['is_holo'] else "Não-Holonômico (Diferencial)"
            print(f"  ✓ {nome} ({status_holo}): {len(s['num_robots'])} configurações de robôs encontradas.")
        else:
            print(f"  ⚠️ {nome}: Nenhum dado completo encontrado.")

    if not stats_carregadas:
        print("❌ Nenhum dado foi encontrado para plotar.")
        return

    # 1. Agrupamento por algoritmos para comparação par a par (Holo vs Não-Holo)
    # Tenta agrupar removendo sufixos _holo, -holo, etc.
    algoritmos_pares = {}
    for nome, item in dados_carregados.items():
        chave_algo = nome.lower().replace('_holo', '').replace('-holo', '').replace('holo', '').strip('_- ')
        if not chave_algo:
            chave_algo = nome
        if chave_algo not in algoritmos_pares:
            algoritmos_pares[chave_algo] = {}
            
        tipo = "Holo" if item['is_holo'] else "Nao_Holo"
        algoritmos_pares[chave_algo][f"{nome} ({tipo})"] = stats_carregadas[nome]

    print("\n📊 [1/4] Gerando gráficos de comparação interna (Holo vs Não-Holo por algoritmo)...")
    for algo, series in algoritmos_pares.items():
        if len(series) >= 2:
            pasta_algo = os.path.join(pasta_saida_base, 'comparacao_algoritmos_interna', algo)
            plotar_comparacao_multipla(series, f"Algoritmo: {algo}", pasta_algo, prefixo_arquivo=f"{algo}_")

    # 2. Comparativo entre todos os Não-Holonômicos
    nao_holo_series = {
        nome: stats_carregadas[nome]
        for nome, item in dados_carregados.items() if not item['is_holo']
    }
    if len(nao_holo_series) > 1:
        print("\n📊 [2/4] Gerando comparativo entre todos os Não-Holonômicos...")
        pasta_nao_holo = os.path.join(pasta_saida_base, 'comparativo_geral_nao_holonomicos')
        plotar_comparacao_multipla(nao_holo_series, "Todos Não-Holonômicos", pasta_nao_holo, prefixo_arquivo="nao_holo_")

    # 3. Comparativo entre todos os Holonômicos
    holo_series = {
        nome: stats_carregadas[nome]
        for nome, item in dados_carregados.items() if item['is_holo']
    }
    if len(holo_series) > 1:
        print("\n📊 [3/4] Gerando comparativo entre todos os Holonômicos...")
        pasta_holo = os.path.join(pasta_saida_base, 'comparativo_geral_holonomicos')
        plotar_comparacao_multipla(holo_series, "Todos Holonômicos", pasta_holo, prefixo_arquivo="holo_")

    # 4. Comparativo Global (Todos juntos)
    print("\n📊 [4/4] Gerando comparativo global (Todas as séries)...")
    pasta_global = os.path.join(pasta_saida_base, 'comparativo_global_todos')
    plotar_comparacao_multipla(stats_carregadas, "Geral Completo", pasta_global, prefixo_arquivo="todos_")

    print(f"\n✨ Processamento concluído! Todos os gráficos foram salvos sob: {pasta_saida_base}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Gera gráficos comparativos de simulações com múltiplos algoritmos, Holo e Não-Holo."
    )
    parser.add_argument(
        "--raiz", "-r",
        default="/home/andersoney/workspace/Logs",
        help="Diretório raiz onde estão os logs ou subpastas de logs (default: /home/andersoney/workspace/Logs ou diretório atual)."
    )
    parser.add_argument(
        "--saida", "-o",
        default="graficos_comparativos",
        help="Diretório onde os gráficos gerados serão salvos (default: ./graficos_comparativos)."
    )
    parser.add_argument(
        "--pastas", "-p",
        nargs="+",
        help="Lista explícita de pastas de logs para comparar (ex: -p saida_v2 saida_v2_holo)."
    )
    args = parser.parse_args()

    diretorios = []
    
    if args.pastas:
        # Modo explícito: o usuário passa exatamente as pastas que quer comparar
        for p in args.pastas:
            caminho = Path(p).resolve()
            nome = caminho.name
            is_holo = any(token in str(caminho).lower() for token in ['holo', 'omni'])
            diretorios.append({
                'nome': nome,
                'caminho': str(caminho),
                'is_holo': is_holo
            })
    else:
        # Modo automático: varre o diretório raiz indicado
        pasta_busca = args.raiz
        if not os.path.exists(pasta_busca):
            # Se /home/andersoney/workspace/Logs não existir, usa o diretório atual do projeto
            pasta_busca = os.getcwd()
            print(f"ℹ️ Diretório '{args.raiz}' não encontrado. Varrendo diretório atual: {pasta_busca}")
            
        diretorios = descobrir_diretorios(pasta_busca)
        
    if not diretorios:
        print("❌ Nenhuma pasta contendo subdiretórios 'nRobots*' foi encontrada.")
        sys.exit(1)

    processar_experimentos(diretorios, os.path.abspath(args.saida))


if __name__ == "__main__":
    main()
