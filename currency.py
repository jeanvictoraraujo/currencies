# %%
import pandas as pd
import requests
import plotly.express as px

# # Defina o intervalo de datas de início e fim
# data_inicio = "01/01/2023"
# data_fim = "31/10/2024"

# # URLs para as moedas (ajuste o intervalo de datas)
# urls = [
#     f"https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda=61&DATAINI={data_inicio}&DATAFIM={data_fim}",
#     f"https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda=57&DATAINI={data_inicio}&DATAFIM={data_fim}",
#     f"https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda=115&DATAINI={data_inicio}&DATAFIM={data_fim}",
#     f"https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda=158&DATAINI={data_inicio}&DATAFIM={data_fim}",
#     f"https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda=159&DATAINI={data_inicio}&DATAFIM={data_fim}",
# ]

# # Baixar os arquivos CSV
# for url in urls:
#     response = requests.get(url)
#     moeda = url.split("ChkMoeda=")[1].split("&")[0]

#     # Criar nome do arquivo, substituindo as barras (/) por hífens (-)
#     nome_arquivo = f"taxas_cambio_{moeda}_{data_inicio.replace('/', '-')}_to_{data_fim.replace('/', '-')}.csv"

#     with open(nome_arquivo, "wb") as file:
#         file.write(response.content)

#     print(f"Arquivo para {moeda} baixado com sucesso!")

# Função para processar cada arquivo
def processar_arquivo_taxas(path):
    # Definir as colunas para o DataFrame
    colunas = [
        "Data",
        "Código_Moeda",
        "Tipo",
        "Moeda",
        "Taxa_Compra",
        "Taxa_Venda",
        "Paridade_Compra",
        "Paridade_Venda",
    ]

    # Carregar o arquivo CSV
    df = pd.read_csv(path, sep=";", encoding="latin1", names=colunas, decimal=",")

    # Função para corrigir a data
    def corrigir_data(data):
        data = str(data)
        if len(data) == 7:
            dia = data[:1]
            mes = data[1:3]
            ano = data[3:]
        elif len(data) == 8:
            dia = data[:2]
            mes = data[2:4]
            ano = data[4:]
        else:
            return None
        return f"{dia}/{mes}/{ano}"

    # Corrigir a coluna 'Data'
    df["Data"] = df["Data"].apply(corrigir_data)

    # Converter a coluna 'Data' para datetime
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")

    # Criar coluna 'Ano_Mes'
    df["Ano_Mes"] = df["Data"].dt.to_period("M")

    df.loc[df['Moeda'] == 'USD', 'Paridade_Venda'] = df.loc[df['Moeda'] == 'USD', 'Taxa_Venda']

    df.loc[df['Moeda'] == 'USD', 'Paridade_Compra'] = df.loc[df['Moeda'] == 'USD', 'Taxa_Compra']

    df.loc[df["Moeda"] == "USD", "Moeda"] = "BRL"

    if 'GBP' in df['Moeda'].unique():
        df.loc[df['Moeda'] == 'GBP', 'Taxa_Compra'] = 1 / df.loc[df['Moeda'] == 'GBP', 'Taxa_Compra']
        df.loc[df['Moeda'] == 'GBP', 'Taxa_Venda'] = 1 / df.loc[df['Moeda'] == 'GBP', 'Taxa_Venda']
        df.loc[df['Moeda'] == 'GBP', 'Paridade_Compra'] = 1 / df.loc[df['Moeda'] == 'GBP', 'Paridade_Compra']
        df.loc[df['Moeda'] == 'GBP', 'Paridade_Venda'] = 1 / df.loc[df['Moeda'] == 'GBP', 'Paridade_Venda']

    if "HKD" in df["Moeda"].unique():
        df.loc[df["Moeda"] == "HKD", "Taxa_Compra"] = (
            1 / df.loc[df["Moeda"] == "HKD", "Taxa_Compra"]
        )
        df.loc[df["Moeda"] == "HKD", "Taxa_Venda"] = (
            1 / df.loc[df["Moeda"] == "HKD", "Taxa_Venda"]
        )
        df.loc[df["Moeda"] == "HKD", "Paridade_Compra"] = (
            1 / df.loc[df["Moeda"] == "HKD", "Paridade_Compra"]
        )
        df.loc[df["Moeda"] == "HKD", "Paridade_Venda"] = (
            1 / df.loc[df["Moeda"] == "HKD", "Paridade_Venda"]
        )

    return df


# Lista de arquivos para processar
arquivos = [
    "taxas_cambio_57_01-01-2023_to_31-10-2024.csv",
    "taxas_cambio_61_01-01-2023_to_31-10-2024.csv",
    "taxas_cambio_115_01-01-2023_to_31-10-2024.csv",
    "taxas_cambio_158_01-01-2023_to_31-10-2024.csv",
    "taxas_cambio_159_01-01-2023_to_31-10-2024.csv",
    # Adicione outros arquivos aqui
]

# Processar todos os arquivos e juntar os resultados
dados_combinados = []
for arquivo in arquivos:
    df_processado = processar_arquivo_taxas(arquivo)
    dados_combinados.append(df_processado)

# Concatenar todos os DataFrames em um único
df_final = pd.concat(dados_combinados, ignore_index=True)

# Copiar os dados da moeda BRL
df_usd = df_final[df_final["Moeda"] == "BRL"].copy()

# Alterar o nome da moeda para 'USD' e ajustar todas as taxas para 1
df_usd["Moeda"] = "USD"
df_usd["Taxa_Compra"] = 1
df_usd["Taxa_Venda"] = 1
df_usd["Paridade_Compra"] = 1
df_usd["Paridade_Venda"] = 1

# Adicionar o DataFrame da moeda USD ao DataFrame original
df_final = pd.concat([df_final, df_usd], ignore_index=True)

# Calcular a média de 'Paridade_Venda' por 'Ano_Mes'

# %%
# Calcular a média da Paridade_Venda por Ano_Mes e Moeda
resultado = (
    df_final.groupby(["Ano_Mes", "Moeda"])["Paridade_Venda"].mean().reset_index()
)

# Calcular a última cotação do mês para cada Moeda e Ano_Mes
ultima_cotacao = (
    df_final.groupby(["Ano_Mes", "Moeda"])["Paridade_Venda"].last().reset_index()
)
ultima_cotacao = ultima_cotacao.rename(
    columns={"Paridade_Venda": "taxa_fechamento_mes"}
)

# Merge para adicionar a coluna taxa_fechamento_mes ao DataFrame resultado
resultado = pd.merge(resultado, ultima_cotacao, on=["Ano_Mes", "Moeda"], how="left")

# Visualizar o resultado final
resultado = resultado.rename(columns={"Paridade_Venda": "taxa_media_mes"})

# %%

import plotly.express as px
import streamlit as st

st.title("Consulta de Taxas de Fechamento e Média")

# Seleção de moeda
moeda_selecionada = st.selectbox("Escolha a moeda:", resultado["Moeda"].unique())

# Seleção de mês
mes_selecionado = st.selectbox("Escolha o mês:", resultado["Ano_Mes"].unique())

# Filtrar o DataFrame com a moeda e o mês selecionados
df_filtrado = resultado[
    (resultado["Moeda"] == moeda_selecionada)
    & (resultado["Ano_Mes"] == mes_selecionado)
]

if not df_filtrado.empty:
    st.write(
        f"Taxa Média de Venda para {moeda_selecionada} no mês {mes_selecionado}: {df_filtrado['taxa_media_mes'].values[0]}"
    )
    st.write(
        f"Taxa de Fechamento para {moeda_selecionada} no mês {mes_selecionado}: {df_filtrado['taxa_fechamento_mes'].values[0]}"
    )

    # Gráfico de Evolução da Moeda (Taxa de Fechamento e Média)
    df_moeda = resultado[resultado["Moeda"] == moeda_selecionada]

    # Converte a coluna 'Ano_Mes' para string para evitar o erro de serialização com Period
    df_moeda["Ano_Mes"] = df_moeda["Ano_Mes"].astype(str)

    # Criar gráfico com duas linhas: uma para a taxa média e outra para a taxa de fechamento
    fig = px.line(
        df_moeda,
        x="Ano_Mes",
        y=["taxa_media_mes", "taxa_fechamento_mes"],
        title=f"Evolução das Taxas de {moeda_selecionada}",
        labels={"Ano_Mes": "Mês", "value": "Taxa", "variable": "Tipo de Taxa"},
    )

    # Exibindo o gráfico
    st.plotly_chart(fig)

else:
    st.write(f"Não há dados para {moeda_selecionada} no mês {mes_selecionado}.")
