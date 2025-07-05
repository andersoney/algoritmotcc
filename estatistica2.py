import pandas as pd
import matplotlib.pyplot as plt

def plot_dois_experimentos(csv_path1, csv_path2, x_col, y_col, label1="Experimento 1", label2="Experimento 2"):
    # Lê os CSVs
    df1 = pd.read_csv(csv_path1, sep=';')
    df2 = pd.read_csv(csv_path2, sep=';')

    # Verifica se as colunas existem
    for df, label in [(df1, label1), (df2, label2)]:
        if x_col not in df.columns or y_col not in df.columns:
            print(f"Colunas disponíveis em {label}: {list(df.columns)}")
            raise ValueError(f"As colunas '{x_col}' ou '{y_col}' não existem no arquivo de {label}.")

    x1, y1 = df1[x_col], df1[y_col]
    x2, y2 = df2[x_col], df2[y_col]

    plt.figure(figsize=(10,6))
    plt.plot(x1, y1, marker='o', label=label1)
    plt.plot(x2, y2, marker='x', label=label2)

    plt.title(f"Comparação: {y_col} vs {x_col}")
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_dois_experimentos(
        "csv_agrupado_com_labels.csv",
        "csv_agrupado_com_labels2.csv",
        "num_robot_dir",
        "numTotalIterations",
        label1="Experimento A",
        label2="Experimento B"
    )
