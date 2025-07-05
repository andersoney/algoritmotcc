import pandas as pd
from pathlib import Path

def agrupar_logs_linhas_com_labels(diretorio_saida, arquivo_destino, labels):
    diretorio = Path(diretorio_saida)
    registros = []

    for pasta_robot in sorted(diretorio.glob("nRobots*")):
        if not pasta_robot.is_dir():
            continue

        num_robot = pasta_robot.name.replace("nRobots", "")

        for arquivo_log in sorted(pasta_robot.glob("logs_*")):
            num_exp = arquivo_log.stem.replace("logs_", "")

            with open(arquivo_log, 'r', encoding='utf-8') as f:
                linhas = [linha.strip() for linha in f if linha.strip()]

            if len(linhas) != len(labels):
                print(f"Aviso: número de linhas ({len(linhas)}) diferente do número de labels ({len(labels)}) em {arquivo_log}. Arquivo ignorado.")
                continue

            registro = {
                'num_robot_dir': int(num_robot),
                'num_exp_file': int(num_exp),
            }

            # associa labels e valores linha a linha
            registro.update(dict(zip(labels, linhas)))

            registros.append(registro)

    if registros:
        df_final = pd.DataFrame(registros)
        df_final.to_csv(arquivo_destino, sep=';', index=False)
        print(f"Arquivo gerado: {arquivo_destino}")
    else:
        print("Nenhum registro válido encontrado.")

if __name__ == "__main__":
    labels_para_linhas = ["numTotalIterations","numMaxIterationsReachGoal + numMaxIterationsExitGoal","numMsgs","numTotalIterationsReachGoal","numTotalIterationsExitGoal","numMaxIterationsReachGoal","numMaxIterationsExitGoal","numTotalStalls"]  # ajuste para os labels corretos
    agrupar_logs_linhas_com_labels("saidas", "csv_agrupado_com_labels.csv", labels_para_linhas)
