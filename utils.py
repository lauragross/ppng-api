from datetime import datetime
import json
import os

DATA_BASE_PATH = 'data_base.txt' # mesmo caminho usado em definir_data_base()

def ler_data_base() -> datetime.date:
    """
    Lê a data base do fechamento salva em 'data_base.txt' e retorna como objeto date.
    :return: data base (datetime.date)
    :raises: FileNotFoundError, ValueError
    """
    if not os.path.exists(DATA_BASE_PATH):
        raise FileNotFoundError("Arquivo com data base não encontrado")
    with open(DATA_BASE_PATH, 'r') as f:
        data_str = f.read().strip()

    try:
        data_formatada = datetime.strptime(data_str, '%d/%m/%Y').date()
        return data_formatada
    except ValueError:
        raise ValueError("Formato inválido da data base. Esperado: dd/mm/aaaa")


PROGRESS_FILE = 'ppng_progresso.json'

def atualizar_progresso(percentual):
    """
    Atualiza o progresso do cálculo da PPNG em um arquivo JSON.
    """
    with open(PROGRESS_FILE,'w') as f:
        json.dump({'progresso': percentual}, f)

def ler_progresso():
    """
    Lê o progresso do cálculo da PPNG a partir do arquivo JSON.
    """
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f).get('progresso', 0)
    return 0
