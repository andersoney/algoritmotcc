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

# Paleta ampla de 30 cores visualmente distintas para evitar repetição mesmo com muitas curvas
CORES = [
    '#1f77b4', '#d62728', '#2ca02c', '#ff7f0e', '#9467bd',
    '#8c564b', '#e377c2', '#17becf', '#bcbd22', '#333333',
    '#003f5c', '#58508d', '#bc5090', '#ff6361', '#ffa600',
    '#2e8b57', '#8a2be2', '#dc143c', '#00ced1', '#ff1493',
    '#708090', '#4682b4', '#d2691e', '#9acd32', '#4b0082',
    '#b22222', '#20b2aa', '#daa520', '#696969', '#000080'
]
MARCADORES = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'X', 'P', 'd']
ESTILOS_LINHA = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 2)), (0, (1, 1)), (0, (5, 1))]


def obter_estilo_serie(idx, total_series):
    """
    Garante que cada série tenha uma cor única (gerando dinamicamente se passar de 30),
    além de marcador e estilo de linha distintos.
    """
    if idx < len(CORES):
        cor = CORES[idx]
    elif plt is not None:
        # Gera cores uniformemente espaçadas no colormap turbo/tab20 para nunca repetir
        cmap = plt.cm.get_cmap('tab20b' if idx % 2 == 0 else 'tab20c')
        cor = cmap((idx % 20) / 20.0)
    else:
        cor = f"C{idx}"
        
    marcador = MARCADORES[idx % len(MARCADORES)]
    estilo = ESTILOS_LINHA[idx % len(ESTILOS_LINHA)]
    return cor, marcador, estilo


import re

def extrair_num_robos_de_caminho(path_obj):
    """
    Percorre as partes do caminho de trás para frente buscando a primeira pasta
    que case com padrão de contagem de robôs (ex: 'robots_20', 'n_200', 'nRobots40').
    Retorna o int ou None.
    """
    padrao = re.compile(r'^(?:.*?[a-zA-Z_-]+)?_?(\d+)$')
    # Não considerar partes como 'm_10', 's3', 'logs_0' como contagem de robôs
    ignorar_prefixos = ('m_', 's', 'cout', 'logs')
    
    for parte in reversed(path_obj.parts):
        parte_lower = parte.lower()
        if any(parte_lower.startswith(p) for p in ignorar_prefixos) and not parte_lower.startswith('n_'):
            continue
        m = padrao.search(parte)
        if m:
            val = int(m.group(1))
            # Valores típicos de contagem de robôs
            return val
    return None


def ler_logs(pasta_base):
    """
    Lê recursivamente todos os arquivos de log ('log_*' ou 'logs_*') da pasta_base,
    inclusive em subpastas aninhadas (ex: robots_20/m_10/log_0, s3/n_60/log_0).
    Retorna um dicionário com as métricas agrupadas por número de robôs.
    """
    dados = {}
    pasta_path = Path(pasta_base)
    
    if not pasta_path.exists():
        print(f"⚠️ Diretório não encontrado: {pasta_base}")
        return dados

    # Encontra recursivamente arquivos de log
    arquivos_log = []
    for padrao in ["**/logs_*", "**/log_*", "logs_*", "log_*"]:
        arquivos_log.extend(pasta_path.glob(padrao))
        
    for arq in sorted(set(arquivos_log)):
        if not arq.is_file():
            continue
        # Ignora arquivos de log de compilação ou saída de terminal .log
        if arq.suffix == '.log':
            continue
            
        # Descobre o número de robôs a partir do caminho
        num_robots = extrair_num_robos_de_caminho(arq.parent)
        if num_robots is None:
            continue
            
        if num_robots not in dados:
            dados[num_robots] = {
                'numTotalStalls': [],
                'reachingTargetTime': [],
                'numMaxIterationsTotal': [],
                'numMsgs': []
            }
            
        try:
            with open(arq, 'r', encoding='utf-8') as f:
                linhas = [l.strip() for l in f if l.strip()]
            
            if len(linhas) >= 9:
                # Trata formatos com e sem num_robots na linha 0
                # Se linha 0 for muito alta (ex: > 10.000), o arquivo não tem num_robots no topo
                tem_cabecalho = False
                try:
                    primeiro_val = int(linhas[0])
                    # se o primeiro valor for exatamente o num_robots, tem cabeçalho
                    if primeiro_val == num_robots:
                        tem_cabecalho = True
                except ValueError:
                    tem_cabecalho = False
                    
                if tem_cabecalho and len(linhas) >= 10:
                    iter_tot = int(linhas[2])
                    msgs = int(linhas[3])
                    stalls = int(linhas[8])
                    time_s = float(linhas[9]) / 1e6
                else:
                    # Formato sem o campo num_robots na linha 0:
                    # 0: numTotalIterations
                    # 1: numMaxIterationsTotal
                    # 2: numMsgs
                    # ...
                    # 7: numTotalStalls
                    # 8: reachingTargetTime
                    iter_tot = int(linhas[1])
                    msgs = int(linhas[2])
                    stalls = int(linhas[7])
                    time_s = float(linhas[8]) / 1e6
                
                dados[num_robots]['numMaxIterationsTotal'].append(iter_tot)
                dados[num_robots]['numMsgs'].append(msgs)
                dados[num_robots]['numTotalStalls'].append(stalls)
                dados[num_robots]['reachingTargetTime'].append(time_s)
        except Exception:
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

    n_series = len(series_dict)
    # Jitter (deslocamento horizontal) para descolar marcadores e barras de erro sobrepostos
    def aplicar_jitter(x_vals, idx, total):
        if total <= 1:
            return x_vals
        # passo proporcional para afastar pontos sobrepostos no eixo X
        offset = (idx - (total - 1) / 2.0) * 0.8
        return [x + offset for x in x_vals]
    
    # 1. Total de Stalls
    plt.figure(figsize=(11, 6))
    for i, (nome, s) in enumerate(series_dict.items()):
        cor, marcador, estilo = obter_estilo_serie(i, n_series)
        x_jittered = aplicar_jitter(s['num_robots'], i, n_series)
        plt.errorbar(x_jittered, s['stalls_mean'], yerr=s['stalls_std'],
                     label=nome, color=cor, marker=marcador, linestyle=estilo,
                     capsize=4, linewidth=2, markersize=7, alpha=0.9)
    plt.xlabel('Número de Robôs', fontsize=12)
    plt.ylabel('Total de Colisões/Stalls (média)', fontsize=12)
    plt.title(f'Comparação: Número de Robôs vs Total de Stalls ({titulo_sufixo})', fontsize=13, fontweight='bold')
    plt.legend(fontsize=9, loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}stalls.png'), dpi=200)
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}stalls.pdf'))
    plt.close()

    # 2. Tempo de Simulação (segundos)
    plt.figure(figsize=(11, 6))
    for i, (nome, s) in enumerate(series_dict.items()):
        cor, marcador, estilo = obter_estilo_serie(i, n_series)
        x_jittered = aplicar_jitter(s['num_robots'], i, n_series)
        plt.errorbar(x_jittered, s['time_mean'], yerr=s['time_std'],
                     label=nome, color=cor, marker=marcador, linestyle=estilo,
                     capsize=4, linewidth=2, markersize=7, alpha=0.9)
    plt.xlabel('Número de Robôs', fontsize=12)
    plt.ylabel('Tempo de Simulação (s)', fontsize=12)
    plt.title(f'Comparação: Número de Robôs vs Tempo de Simulação ({titulo_sufixo})', fontsize=13, fontweight='bold')
    plt.legend(fontsize=9, loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}tempo_simulacao.png'), dpi=200)
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}tempo_simulacao.pdf'))
    plt.close()

    # 3. Iterações Máximas
    plt.figure(figsize=(11, 6))
    for i, (nome, s) in enumerate(series_dict.items()):
        cor, marcador, estilo = obter_estilo_serie(i, n_series)
        x_jittered = aplicar_jitter(s['num_robots'], i, n_series)
        plt.errorbar(x_jittered, s['iterations_mean'], yerr=s['iterations_std'],
                     label=nome, color=cor, marker=marcador, linestyle=estilo,
                     capsize=4, linewidth=2, markersize=7, alpha=0.9)
    plt.xlabel('Número de Robôs', fontsize=12)
    plt.ylabel('Máximo de Iterações (ReachGoal + ExitGoal)', fontsize=12)
    plt.title(f'Comparação: Número de Robôs vs Máx. Iterações ({titulo_sufixo})', fontsize=13, fontweight='bold')
    plt.legend(fontsize=9, loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}iteracoes.png'), dpi=200)
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}iteracoes.pdf'))
    plt.close()

    # 4. Painel Combinado (3 subplots horizontais)
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))
    
    # Subplot 1: Stalls
    for i, (nome, s) in enumerate(series_dict.items()):
        cor, marcador, estilo = obter_estilo_serie(i, n_series)
        x_jittered = aplicar_jitter(s['num_robots'], i, n_series)
        axes[0].errorbar(x_jittered, s['stalls_mean'], yerr=s['stalls_std'],
                         label=nome, color=cor, marker=marcador, linestyle=estilo,
                         capsize=3, linewidth=1.8, markersize=6, alpha=0.9)
    axes[0].set_xlabel('Número de Robôs', fontsize=11)
    axes[0].set_ylabel('Total de Stalls', fontsize=11)
    axes[0].set_title('Total de Stalls', fontsize=12, fontweight='bold')
    axes[0].legend(fontsize=8, loc='best')
    axes[0].grid(True, alpha=0.3)

    # Subplot 2: Tempo
    for i, (nome, s) in enumerate(series_dict.items()):
        cor, marcador, estilo = obter_estilo_serie(i, n_series)
        x_jittered = aplicar_jitter(s['num_robots'], i, n_series)
        axes[1].errorbar(x_jittered, s['time_mean'], yerr=s['time_std'],
                         label=nome, color=cor, marker=marcador, linestyle=estilo,
                         capsize=3, linewidth=1.8, markersize=6, alpha=0.9)
    axes[1].set_xlabel('Número de Robôs', fontsize=11)
    axes[1].set_ylabel('Tempo de Simulação (s)', fontsize=11)
    axes[1].set_title('Tempo para Conclusão (s)', fontsize=12, fontweight='bold')
    axes[1].legend(fontsize=8, loc='best')
    axes[1].grid(True, alpha=0.3)

    # Subplot 3: Iterações
    for i, (nome, s) in enumerate(series_dict.items()):
        cor, marcador, estilo = obter_estilo_serie(i, n_series)
        x_jittered = aplicar_jitter(s['num_robots'], i, n_series)
        axes[2].errorbar(x_jittered, s['iterations_mean'], yerr=s['iterations_std'],
                         label=nome, color=cor, marker=marcador, linestyle=estilo,
                         capsize=3, linewidth=1.8, markersize=6, alpha=0.9)
    axes[2].set_xlabel('Número de Robôs', fontsize=11)
    axes[2].set_ylabel('Máx. Iterações', fontsize=11)
    axes[2].set_title('Iterações Máximas', fontsize=12, fontweight='bold')
    axes[2].legend(fontsize=8, loc='best')
    axes[2].grid(True, alpha=0.3)
    axes[2].grid(True, alpha=0.3)

    plt.suptitle(f'Visão Geral Consolidada ({titulo_sufixo})', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}painel_combinado.png'), dpi=200, bbox_inches='tight')
    plt.savefig(os.path.join(pasta_saida, f'{prefixo_arquivo}painel_combinado.pdf'), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráficos salvos em: {pasta_saida} (prefixo: '{prefixo_arquivo}')")


def extrair_identificador_algoritmo(caminho_ou_nome):
    """
    Extrai o nome do algoritmo a partir do caminho ou nome da pasta,
    removendo marcações de holonomia/diferencial e prefixos como 'saida_' ou 'logs_'.
    Exemplos:
      'SQF/holo' -> 'SQF'
      'SQF/diff' -> 'SQF'
      'saida_sqf_holo' -> 'sqf'
      'PCCEEV2_holo' -> 'pcceev2'
    """
    partes = Path(caminho_ou_nome).parts
    tokens_ignorar = {'holo', 'holonomico', 'omni', 'diff', 'diferencial', 'nao_holo', 'nao-holo', 'saida', 'saidas', 'logs'}
    
    # Procura da direita para a esquerda a primeira parte que seja o nome real do algoritmo
    for parte in reversed(partes):
        limpo = parte.lower().replace('_holo', '').replace('-holo', '').replace('_diff', '').replace('-diff', '').strip('_- ')
        if limpo.startswith('saida_'):
            limpo = limpo.replace('saida_', '')
        if limpo.startswith('logs_'):
            limpo = limpo.replace('logs_', '')
        if limpo and limpo not in tokens_ignorar:
            return limpo
            
    # Fallback caso tudo tenha sido filtrado
    return str(partes[-1]).lower()


def descobrir_diretorios(diretorio_raiz):
    """
    Percorre recursivamente toda a árvore de diretórios em qualquer nível de profundidade
    e detecta pastas que contenham subpastas de robôs ou arquivos de logs ('log_*' ou 'logs_*').
    Identifica o nome do algoritmo e se a configuração é holonômica ou diferencial.
    """
    raiz = Path(diretorio_raiz).resolve()
    candidatos = set()
    
    # Procura arquivos de log em qualquer profundidade
    padroes_log = ["**/logs_*", "**/log_*", "logs_*", "log_*"]
    arquivos_encontrados = []
    for padrao in padroes_log:
        arquivos_encontrados.extend(raiz.glob(padrao))
        
    for arq in arquivos_encontrados:
        if not arq.is_file() or arq.suffix == '.log':
            continue
            
        # Percorre os ancestrais do arquivo para achar o diretório raiz do experimento/algoritmo
        # Exemplo: Logs/nonholo/NoCoordAlt/SQF/robots_20/m_10/log_0
        # O pai direto é m_10, o avô é robots_20, e a raiz do algoritmo é SQF (ou NoCoordAlt/SQF)
        partes = list(arq.parents)
        for p in partes:
            # Se 'p' contém subpastas com contagem de robôs (diretas ou indiretas)
            # e não é uma subpasta de variação (como m_* ou n_*), é candidato a raiz de experimento
            nome_p = p.name.lower()
            if nome_p in ('saidas', 'cout', 'venv') or nome_p.startswith('m_') or nome_p.startswith('s'):
                continue
            if extrair_num_robos_de_caminho(p) is not None:
                continue
            if p == raiz.parent:
                continue
            candidatos.add(p)
            break
            
    resultados = []
    for c in sorted(candidatos):
        try:
            rel = c.relative_to(raiz)
            nome = str(rel) if str(rel) != "." else c.name
        except ValueError:
            nome = c.name
            
        # Determina se é holonômico baseado em qualquer parte do caminho
        caminho_str_lower = str(c).lower()
        is_holo = any(token in caminho_str_lower for token in ['holo', 'omni'])
        algo_id = extrair_identificador_algoritmo(c)
        
        resultados.append({
            'nome': nome,
            'caminho': str(c),
            'is_holo': is_holo,
            'algoritmo': algo_id
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
            algo = item.get('algoritmo', nome)
            print(f"  ✓ {nome} [Algoritmo: {algo}] ({status_holo}): {len(s['num_robots'])} configurações de robôs encontradas.")
        else:
            print(f"  ⚠️ {nome}: Nenhum dado completo encontrado.")

    if not stats_carregadas:
        print("❌ Nenhum dado foi encontrado para plotar.")
        return

    # 1. Agrupamento por algoritmos para comparação par a par (Holo vs Não-Holo)
    algoritmos_pares = {}
    for nome, item in dados_carregados.items():
        chave_algo = item.get('algoritmo') or extrair_identificador_algoritmo(nome)
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
