import sqlite3
import pandas as pd

def importar_contratos_parquet(parquet_path='base_emi_ress.parquet', db_path='ppng-api.db'):
    # Lê o arquivo Parquet
    df = pd.read_parquet(parquet_path)

    #print(f"{len(df.columns)} colunas lidas:", df.columns.tolist()) # Diagnóstico rápido
    #print(df.dtypes)  # Diagnóstico rápido

    # Corrige os tipos incompatíveis com SQLite
    df['uyRess'] = df['uyRess'].astype('Int64').astype(str)
    df['vigApol'] = df['vigApol'].astype('Int64').astype(str)

    colunas_data = ['uyStartRess', 'uyEndRess', 'accFrom', 'accTo', 'iniRisco', 'fimRisco', 'dtEmiss']
    for col in colunas_data:
        df[col] = df[col].dt.strftime('%Y-%m-%d')

    colunas_texto = ['contratoRess', 'tipoContratoRess', 'baseCessao', 'baseDif',
                     'tipoLanc', 'entryCode', 'grupo', 'mainClass', 'section', 'moeda']
    for col in colunas_texto:
        df[col] = df[col].astype(str)

    # Substitui NaNs por None
    df = df.where(pd.notnull(df), None)

    # Conexão com SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS base_emi_ress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contratoRess TEXT,
            uyRess TEXT,
            uyStartRess TEXT,
            uyEndRess TEXT,
            accFrom TEXT,
            accTo TEXT,
            iniRisco TEXT,
            fimRisco TEXT,
            tipoContratoRess TEXT,
            baseCessao TEXT,
            vigApol TEXT,
            baseDif TEXT,
            tipoLanc TEXT,
            entryCode TEXT,
            grupo TEXT,
            mainClass TEXT,
            section TEXT,
            moeda TEXT,
            dtEmiss TEXT,
            premRessMO REAL,
            premRessCE REAL,
            premRessCA REAL
        )
    ''')

    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO base_emi_ress (
                contratoRess, uyRess, uyStartRess, uyEndRess,
                accFrom, accTo, iniRisco, fimRisco,
                tipoContratoRess, baseCessao, vigApol, baseDif,
                tipoLanc, entryCode,
                grupo, mainClass, section, moeda,
                dtEmiss, premRessMO, premRessCE, premRessCA
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['contratoRess'], row['uyRess'], row['uyStartRess'], row['uyEndRess'],
            row['accFrom'], row['accTo'], row['iniRisco'], row['fimRisco'],
            row['tipoContratoRess'], row['baseCessao'], row['vigApol'], row['baseDif'],
            row['tipoLanc'], row['entryCode'],
            row['grupo'], row['mainClass'], row['section'], row['moeda'],
            row['dtEmiss'], row['premRessMO'], row['premRessCE'], row['premRessCA']
        ))

    conn.commit()
    conn.close()
    print("Base de contratos importada com sucesso.")

# Executa diretamente
if __name__ == '__main__':
    importar_contratos_parquet()
