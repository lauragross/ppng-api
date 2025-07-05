
import sqlite3
import pandas as pd

def importar_contratos_parquet(parquet_path='base_emi_ress.parquet', db_path='ppng-api.db'):
    df = pd.read_parquet(parquet_path)

    df['uyRess'] = df['uyRess'].astype('Int64').astype(str)
    df['vigApol'] = df['vigApol'].astype('Int64').astype(str)

    colunas_data = ['uyStartRess', 'uyEndRess', 'accFrom', 'accTo', 'iniRisco', 'fimRisco', 'dtEmiss']
    for col in colunas_data:
        df[col] = df[col].dt.strftime('%Y-%m-%d')

    colunas_texto = ['contratoRess', 'tipoContratoRess', 'baseCessao', 'baseDif',
                     'tipoLanc', 'entryCode', 'grupo', 'mainClass', 'section', 'moeda']
    for col in colunas_texto:
        df[col] = df[col].astype(str)

    df = df.where(pd.notnull(df), None)

    conn = sqlite3.connect(db_path)
    df.to_sql("base_emi_ress", conn, if_exists="replace", index=False)
    conn.close()
    print("Base de contratos importada com sucesso.")

if __name__ == '__main__':
    importar_contratos_parquet()
