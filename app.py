from flasgger import Swagger
from flask import Flask, request, jsonify, render_template, make_response
from datetime import datetime
import sqlite3
import pandas as pd
from flask_cors import CORS

# arquivos internos
from utils import ler_data_base, atualizar_progresso, ler_progresso
from models import carregar_db, calcular_ppng

app = Flask(__name__)
CORS(app)
Swagger(app)

DATA_BASE_PATH = 'data_base.txt'  # arquivo local para armazenar a data

@app.route('/data_base_fechamento', methods=['POST'])
def definir_data_base():
    """
    Define a data base do fechamento (formato: 'dd/mm/aaaa') e salva em arquivo local.
    ---
    tags:
      - Parâmetros
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            data_base:
              type: string
              example: "31/05/2025"
    responses:
      200:
        description: Data base definida com sucesso
        examples:
          application/json: {
            "mensagem": "Data Base definida com sucesso.",
            "data_base": "31/05/2025"
          }
      400:
        description: Data inválida
    """
    dados = request.get_json()
    data_str = dados.get('data_base')

    try:
        # Verifica se a data é válida
        data_formatada = datetime.strptime(data_str, '%d/%m/%Y').date()

        # Salva a data em um arquivo
        with open(DATA_BASE_PATH, 'w') as f:
            f.write(data_str)

        return jsonify({
            "mensagem": "Data Base definida com sucesso.",
            "data_base": data_str
        }), 200

    except Exception as e:
        return jsonify({
            "erro": "Data Inválida. Use o formato dd/mm/aaaa.",
            "detalhes": str(e)
        }), 400

@app.route('/calcular_ppng', methods=['POST'])
def rota_calcular_ppng():
    """
    Carrega o arquivo base_emi_ress.parquet para o banco de dados ppng-api.db, calcula a PPNG dos contratos, salva a base completa no banco e retorna a versão agrupada.
    ---
    tags:
      - Cálculo
    responses:
      200:
        description: Cálculo concluído com sucesso (retorna primeiros 10 registros agrupados)
        examples:
          application/json: [
            {
              "contratoRess": "ABC123",
              "grupo": "Grupo 1",
              "ppngRessCE": 12000.50,
              ...
            }
          ]
      500:
        description: Erro durante o cálculo
    """
    try:
        atualizar_progresso(0) # Início

        # 1. Lê a data base salva
        import database
        database.importar_contratos_parquet()
        atualizar_progresso(10)
        
        data_base = ler_data_base()
        atualizar_progresso(15)

        # 2. Carrega a base de dados original
        df = carregar_db("ppng-api.db", "base_emi_ress")
        atualizar_progresso(30)

        # 3. Calcula a PPNG
        df_calculado = calcular_ppng(df, data_base)
        atualizar_progresso(60)

        # 4. Salva a base completa no banco com nome ppng_YYYYMM
        nome_tabela_ppng = f"ppng_{data_base.strftime('%Y%m')}"
        conn = sqlite3.connect("ppng-api.db")
        df_calculado.to_sql(nome_tabela_ppng, conn, if_exists="replace", index=False)
        atualizar_progresso(75)

        # 5. Cria a versão reduzida (sem colunas técnicas)
        colunas_excluir = ["accFrom", "accTo", "iniRisco", "fimRisco"]
        df_menor = df_calculado.drop(columns=colunas_excluir, errors="ignore")
        atualizar_progresso(85)

        # 6. Agrupa somando os valores monetários
        colunas_valores = ["premRessMO", "premRessCE", "premRessCA", "ppngRessMO", "ppngRessCE", "ppngRessCA", "varCambPPNG"]
        colunas_grupo = [col for col in df_menor.columns if col not in colunas_valores]
        df_menor = df_menor.groupby(colunas_grupo, as_index=False)[colunas_valores].sum()
        atualizar_progresso(95)

        # 7. Retorna o resultado agrupado
        resultado = df_menor.to_dict(orient="records")
        atualizar_progresso(100)
        return jsonify(resultado[:10]), 200


    except Exception as e:
        atualizar_progresso(0) # Reinicia em caso de erro
        return jsonify({
            "erro": "Erro ao calcular a PPNG",
            "detalhes": str(e)
        }), 500

@app.route('/analisar_ppng', methods=['GET'])
def rota_analisar_ppng():
    """
    Retorna uma página HTML com a análise da PPNG agrupada por grupo e moeda.
    ---
    tags:
      - Análise
    responses:
      200:
        description: Página HTML com resumos da PPNG gerada com sucesso
        content:
          text/html:
            schema:
              type: string
        examples:
          text/html: "<html><body>Análise da PPNG</body></html>"
      500:
        description: Erro ao gerar a análise da PPNG
    """
    try:
        data_base = ler_data_base()
        nome_tabela = f"ppng_{data_base.strftime('%Y%m')}"

        conn = sqlite3.connect('ppng-api.db')
        df = pd.read_sql_query(f'SELECT * FROM {nome_tabela}', conn)
        conn.close()

        colunas_soma = ["ppngRessCE", "ppngRessCA", "varCambPPNG"]
        resumo_grupo = df.groupby("grupo", as_index=False)[colunas_soma].sum()
        resumo_moeda = df.groupby("moeda", as_index=False)[colunas_soma].sum()

        html = render_template(
            "analise_ppng.html",
            data_base=data_base.strftime("%d/%m/%Y"),
            resumo_grupo=resumo_grupo.to_dict(orient="records"),
            resumo_moeda=resumo_moeda.to_dict(orient="records")
        )

        # Força UTF-8 na resposta
        response = make_response(html)
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response

    except Exception as e:
        return f"<h3>Erro ao gerar análise: {str(e)}</h3>", 500

@app.route('/progresso_ppng', methods=['GET'])
def progresso_ppng():
    """
    Retorna o progresso atual do cálculo da PPNG (0 a 100).
    ---
    tags:
      - Progresso
    responses:
      200:
        description: Progresso retornado com sucesso
        examples:
          application/json: { "progresso": 85 }
    """
    progresso = ler_progresso()
    return jsonify({'progresso': progresso}), 200

# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)


