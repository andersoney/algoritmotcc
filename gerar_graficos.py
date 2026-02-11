import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def ler_logs(pasta_base):
    """
    Lê todos os arquivos de log de uma pasta e retorna um dicionário
    com os dados agrupados por número de robôs.
    """
    dados = {}
    
    # Percorre todas as subpastas nRobotsXXX
    for pasta in os.listdir(pasta_base):
        if pasta.startswith('nRobots') and os.path.isdir(os.path.join(pasta_base, pasta)):
            num_robots = int(pasta.replace('nRobots', ''))
            dados[num_robots] = {
                'numTotalStalls': [],
                'reachingTargetTime': [],
                'numMaxIterationsTotal': []  # numMaxIterationsReachGoal + numMaxIterationsExitGoal
            }
            
            pasta_completa = os.path.join(pasta_base, pasta)
            
            # Lê todos os arquivos logs_X
            for arquivo in os.listdir(pasta_completa):
                if arquivo.startswith('logs_'):
                    caminho_arquivo = os.path.join(pasta_completa, arquivo)
                    try:
                        with open(caminho_arquivo, 'r') as f:
                            linhas = f.readlines()
                            if len(linhas) >= 10:
                                # Índices baseados na estrutura descrita:
                                # 0: num_robots
                                # 1: numTotalIterations
                                # 2: numMaxIterationsReachGoal + numMaxIterationsExitGoal
                                # 3: numMsgs
                                # 4: numTotalIterationsReachGoal
                                # 5: numTotalIterationsExitGoal
                                # 6: numMaxIterationsReachGoal
                                # 7: numMaxIterationsExitGoal
                                # 8: numTotalStalls
                                # 9: reachingTargetTime
                                
                                numMaxIterationsTotal = int(linhas[2].strip())
                                numTotalStalls = int(linhas[8].strip())
                                reachingTargetTime = int(linhas[9].strip())
                                
                                dados[num_robots]['numTotalStalls'].append(numTotalStalls)
                                dados[num_robots]['reachingTargetTime'].append(reachingTargetTime)
                                dados[num_robots]['numMaxIterationsTotal'].append(numMaxIterationsTotal)
                    except Exception as e:
                        print(f"Erro ao ler {caminho_arquivo}: {e}")
    
    return dados

def calcular_medias(dados):
    """
    Calcula a média e desvio padrão para cada métrica por número de robôs.
    """
    resultados = {
        'num_robots': [],
        'numTotalStalls_media': [],
        'numTotalStalls_std': [],
        'reachingTargetTime_media': [],
        'reachingTargetTime_std': [],
        'numMaxIterationsTotal_media': [],
        'numMaxIterationsTotal_std': []
    }
    
    for num_robots in sorted(dados.keys()):
        resultados['num_robots'].append(num_robots)
        
        stalls = dados[num_robots]['numTotalStalls']
        times = dados[num_robots]['reachingTargetTime']
        iterations = dados[num_robots]['numMaxIterationsTotal']
        
        resultados['numTotalStalls_media'].append(np.mean(stalls) if stalls else 0)
        resultados['numTotalStalls_std'].append(np.std(stalls) if stalls else 0)
        
        resultados['reachingTargetTime_media'].append(np.mean(times) if times else 0)
        resultados['reachingTargetTime_std'].append(np.std(times) if times else 0)
        
        resultados['numMaxIterationsTotal_media'].append(np.mean(iterations) if iterations else 0)
        resultados['numMaxIterationsTotal_std'].append(np.std(iterations) if iterations else 0)
    
    return resultados

def gerar_graficos(dados_v1, dados_v2, pasta_saida='.'):
    """
    Gera os 3 gráficos comparativos entre v1 e v2.
    """
    # Calcula médias
    resultados_v1 = calcular_medias(dados_v1)
    resultados_v2 = calcular_medias(dados_v2)
    
    # Configuração geral dos gráficos
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # ==================== GRÁFICO 1: num_robots vs numTotalStalls ====================
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.errorbar(resultados_v1['num_robots'], resultados_v1['numTotalStalls_media'], 
                yerr=resultados_v1['numTotalStalls_std'], 
                label='Versão 1 (saida_v1)', marker='o', capsize=3, linewidth=2, markersize=6)
    ax.errorbar(resultados_v2['num_robots'], resultados_v2['numTotalStalls_media'], 
                yerr=resultados_v2['numTotalStalls_std'], 
                label='Versão 2 (saida_v2)', marker='s', capsize=3, linewidth=2, markersize=6)
    
    ax.set_xlabel('Número de Robôs', fontsize=12)
    ax.set_ylabel('Total de Stalls (média)', fontsize=12)
    ax.set_title('Comparação: Número de Robôs vs Total de Stalls', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, 'grafico_numTotalStalls.png'), dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(pasta_saida, 'grafico_numTotalStalls.pdf'), bbox_inches='tight')
    print("Gráfico 1 (numTotalStalls) salvo!")
    plt.close()
    
    # ==================== GRÁFICO 2: num_robots vs reachingTargetTime ====================
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Convertendo para segundos (assumindo que está em nanosegundos)
    times_v1 = [t / 1e9 for t in resultados_v1['reachingTargetTime_media']]
    times_v1_std = [t / 1e9 for t in resultados_v1['reachingTargetTime_std']]
    times_v2 = [t / 1e9 for t in resultados_v2['reachingTargetTime_media']]
    times_v2_std = [t / 1e9 for t in resultados_v2['reachingTargetTime_std']]
    
    ax.errorbar(resultados_v1['num_robots'], times_v1, 
                yerr=times_v1_std, 
                label='Versão 1 (saida_v1)', marker='o', capsize=3, linewidth=2, markersize=6)
    ax.errorbar(resultados_v2['num_robots'], times_v2, 
                yerr=times_v2_std, 
                label='Versão 2 (saida_v2)', marker='s', capsize=3, linewidth=2, markersize=6)
    
    ax.set_xlabel('Número de Robôs', fontsize=12)
    ax.set_ylabel('Tempo para Alcançar Alvo - segundos (média)', fontsize=12)
    ax.set_title('Comparação: Número de Robôs vs Tempo para Alcançar Alvo', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, 'grafico_reachingTargetTime.png'), dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(pasta_saida, 'grafico_reachingTargetTime.pdf'), bbox_inches='tight')
    print("Gráfico 2 (reachingTargetTime) salvo!")
    plt.close()
    
    # ==================== GRÁFICO 3: num_robots vs numMaxIterationsTotal ====================
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.errorbar(resultados_v1['num_robots'], resultados_v1['numMaxIterationsTotal_media'], 
                yerr=resultados_v1['numMaxIterationsTotal_std'], 
                label='Versão 1 (saida_v1)', marker='o', capsize=3, linewidth=2, markersize=6)
    ax.errorbar(resultados_v2['num_robots'], resultados_v2['numMaxIterationsTotal_media'], 
                yerr=resultados_v2['numMaxIterationsTotal_std'], 
                label='Versão 2 (saida_v2)', marker='s', capsize=3, linewidth=2, markersize=6)
    
    ax.set_xlabel('Número de Robôs', fontsize=12)
    ax.set_ylabel('Máximo de Iterações Total (média)', fontsize=12)
    ax.set_title('Comparação: Número de Robôs vs Máximo de Iterações (ReachGoal + ExitGoal)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, 'grafico_numMaxIterationsTotal.png'), dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(pasta_saida, 'grafico_numMaxIterationsTotal.pdf'), bbox_inches='tight')
    print("Gráfico 3 (numMaxIterationsTotal) salvo!")
    plt.close()
    
    # ==================== GRÁFICO COMBINADO (3 subplots) ====================
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Subplot 1: numTotalStalls
    axes[0].errorbar(resultados_v1['num_robots'], resultados_v1['numTotalStalls_media'], 
                     yerr=resultados_v1['numTotalStalls_std'], 
                     label='V1', marker='o', capsize=3, linewidth=2, markersize=5)
    axes[0].errorbar(resultados_v2['num_robots'], resultados_v2['numTotalStalls_media'], 
                     yerr=resultados_v2['numTotalStalls_std'], 
                     label='V2', marker='s', capsize=3, linewidth=2, markersize=5)
    axes[0].set_xlabel('Número de Robôs', fontsize=11)
    axes[0].set_ylabel('Total de Stalls', fontsize=11)
    axes[0].set_title('Total de Stalls', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Subplot 2: reachingTargetTime
    axes[1].errorbar(resultados_v1['num_robots'], times_v1, 
                     yerr=times_v1_std, 
                     label='V1', marker='o', capsize=3, linewidth=2, markersize=5)
    axes[1].errorbar(resultados_v2['num_robots'], times_v2, 
                     yerr=times_v2_std, 
                     label='V2', marker='s', capsize=3, linewidth=2, markersize=5)
    axes[1].set_xlabel('Número de Robôs', fontsize=11)
    axes[1].set_ylabel('Tempo (segundos)', fontsize=11)
    axes[1].set_title('Tempo para Alcançar Alvo', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Subplot 3: numMaxIterationsTotal
    axes[2].errorbar(resultados_v1['num_robots'], resultados_v1['numMaxIterationsTotal_media'], 
                     yerr=resultados_v1['numMaxIterationsTotal_std'], 
                     label='V1', marker='o', capsize=3, linewidth=2, markersize=5)
    axes[2].errorbar(resultados_v2['num_robots'], resultados_v2['numMaxIterationsTotal_media'], 
                     yerr=resultados_v2['numMaxIterationsTotal_std'], 
                     label='V2', marker='s', capsize=3, linewidth=2, markersize=5)
    axes[2].set_xlabel('Número de Robôs', fontsize=11)
    axes[2].set_ylabel('Máx. Iterações', fontsize=11)
    axes[2].set_title('Máx. Iterações (ReachGoal + ExitGoal)', fontsize=12, fontweight='bold')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, 'grafico_combinado.png'), dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(pasta_saida, 'grafico_combinado.pdf'), bbox_inches='tight')
    print("Gráfico combinado salvo!")
    plt.close()

def main():
    # Diretório base (onde está o script)
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    
    # Caminhos das pastas de saída
    pasta_v1 = os.path.join(diretorio_base, 'saida_v1')
    pasta_v2 = os.path.join(diretorio_base, 'saida_v2')
    
    # Pasta para salvar os gráficos
    pasta_graficos = os.path.join(diretorio_base, 'graficos')
    os.makedirs(pasta_graficos, exist_ok=True)
    
    print("Lendo logs da versão 1 (saida_v1)...")
    dados_v1 = ler_logs(pasta_v1)
    print(f"  Encontrados dados para {len(dados_v1)} configurações de robôs")
    
    print("Lendo logs da versão 2 (saida_v2)...")
    dados_v2 = ler_logs(pasta_v2)
    print(f"  Encontrados dados para {len(dados_v2)} configurações de robôs")
    
    print("\nGerando gráficos...")
    gerar_graficos(dados_v1, dados_v2, pasta_graficos)
    
    print(f"\n✅ Todos os gráficos foram salvos na pasta: {pasta_graficos}")
    print("Arquivos gerados:")
    print("  - grafico_numTotalStalls.png / .pdf")
    print("  - grafico_reachingTargetTime.png / .pdf")
    print("  - grafico_numMaxIterationsTotal.png / .pdf")
    print("  - grafico_combinado.png / .pdf")

if __name__ == '__main__':
    main()
