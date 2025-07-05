import pandas as pd
import matplotlib.pyplot as plt

def plot_csv(csv_path, x_col, y_col):
    # Lê o CSV com cabeçalho
    df = pd.read_csv(csv_path)

    # Verifica se as colunas existem
    if x_col not in df.columns or y_col not in df.columns:
        print(f"Colunas disponíveis: {list(df.columns)}")
        raise ValueError(f"As colunas '{x_col}' ou '{y_col}' não existem no arquivo.")

    # Pega os dados das colunas
    x = df[x_col]
    y = df[y_col]

    # Cria o gráfico
    plt.figure(figsize=(10,6))
    plt.plot(x, y, marker='o')
    plt.title(f"Gráfico de {y_col} vs {x_col}")
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Exemplo de uso
    caminho_csv = "PCCEEV2_SAIDA/logs.csv"
    coluna_x = "num_robots"
    coluna_y = "reachingTargetTime"
    plot_csv(caminho_csv, coluna_x, coluna_y)
