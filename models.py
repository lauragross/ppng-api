import sqlite3
import pandas as pd
from datetime import datetime, date

def carregar_db(db_path: str, tabela: str) -> pd.DataFrame:
    """
    Lê uma tabela de um banco de dados SQLite e retorna como DataFrame.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * from {tabela}", conn)
    conn.close()
    return df

def calcular_ppng(df: pd.DataFrame, data_base: str) -> pd.DataFrame:
    """
    Calcula a PPNG e a variação cambial para cada contrato.
    """

    if isinstance(data_base, str):
        data_base = datetime.strptime(data_base, "%d/%m/%Y").date()

    def formato_valor(valor_str):
        if isinstance(valor_str, str):
            valor_str = valor_str.replace(".", "").replace(",", ".")
        return round(float(valor_str), 2)

    def to_date(value):
        if pd.isna(value):
            raise ValueError("Data vazia ou nula detectada")
        if isinstance(value, str):
            value = value.strip()
            for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"String de data inválida: {value}")
        elif isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        else:
            raise ValueError(f"Tipo inesperado: {type(value)}")

    df["dtEmiss"] = df["dtEmiss"].apply(to_date)
    df = df[df["dtEmiss"] <= data_base].copy()
    df.drop("dtEmiss", axis=1, inplace=True)

    colunas_valores = ['premRessMO', 'premRessCE', 'premRessCA']
    colunas_grupo = [col for col in df.columns if col not in colunas_valores]

    for col in colunas_valores:
        df[col] = df[col].apply(formato_valor)

    df = df.groupby(colunas_grupo, as_index=False)[colunas_valores].sum()

    def calcular(row):
        ini_risco = to_date(row["iniRisco"])
        fim_risco = to_date(row["fimRisco"])
        premio_ress_mo = row["premRessMO"]
        premio_ress_ce = row["premRessCE"]
        premio_ress_ca = row["premRessCA"]
        tipo_contrato_ress = str(row["tipoContratoRess"])
        tipo_lanc = str(row["tipoLanc"])
        base_cessao = str(row["baseCessao"])

        dias_restantes = (fim_risco - data_base).days
        dias_total = (fim_risco - ini_risco).days
        if dias_total <= 0:
            dias_total = 1
        if tipo_contrato_ress == 'Facultativo' or (
            tipo_contrato_ress == 'Não Proporcional' and base_cessao == 'Losses Occurring'
        ):
            dias_total += 1

        if fim_risco <= data_base or tipo_lanc == 'Reintegração':
            ppng_ress_mo = ppng_ress_ce = ppng_ress_ca = 0
        elif ini_risco > data_base:
            ppng_ress_mo = premio_ress_mo
            ppng_ress_ce = premio_ress_ce
            ppng_ress_ca = premio_ress_ca
        else:
            ppng_ress_mo = round(premio_ress_mo * dias_restantes / dias_total, 2)
            ppng_ress_ce = round(premio_ress_ce * dias_restantes / dias_total, 2)
            ppng_ress_ca = round(premio_ress_ca * dias_restantes / dias_total, 2)

        var_camb_ppng = round(ppng_ress_ca - ppng_ress_ce, 2)
        return pd.Series([ppng_ress_mo, ppng_ress_ce, ppng_ress_ca, var_camb_ppng])

    df[["ppngRessMO", "ppngRessCE", "ppngRessCA", "varCambPPNG"]] = df.apply(calcular, axis=1)
    return df
