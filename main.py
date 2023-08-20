import pandas as pd
import numpy as np
import sqlite3
import config


def cep_gap_finder(range_remove: list, inicio_espectro: int, fim_espectro: int) -> dict:
    '''
    Analisa dentro de espectro de CEPs possíveis as lacunas existentes.
    :param range_remove: Lista de intervalos de CEPs a serem desconsiderados.
    :param inicio_espectro: Inicio do espectro de CEPs a ser analisado.
    :param fim_espectro: fim do espectro de CEPs a ser analisado.
    :return: Dict com os intervalor de lacunas encontradas.
    '''

    # Crie um array NumPy a partir dos CEPs possiveis, dentro do intervalo informado
    # Começa em 0 para coincidir com os indices.
    espectro_cep = np.array(list(range(0, fim_espectro + 1)))

    # Adiciona para marcar para eliminação os CEPs de 0 ao 'inicio'.
    intervalo_remover = range_remove
    intervalo_remover.append((0, inicio_espectro))

    # Crie um array booleano marcando os elementos que não estão nos intervalos informados no CSV
    indices_manter = np.ones(len(espectro_cep), dtype=bool)
    for start, end in intervalo_remover:
        indices_manter[start:end + 1] = False

    # Crie um novo array apenas com os elementos que não foram marcados para remoção
    espectro_cep_filtrados = espectro_cep[indices_manter]

    # Converte o array NumPy de volta para uma lista
    espectro_cep_filtrados = espectro_cep_filtrados.tolist()

    # Cria lista para agrupar os CEPs sequenciais em intervalos
    range_inicio, range_fim = [], []

    # Adiciona o primeiro elemento como CEP inicial do primeiro intervalo
    range_inicio.append(espectro_cep_filtrados[0])

    # Grava o elemento anterior, começando com o primeiro da lista - 1 para ser comparado com o elemento atual do loop
    anterior = espectro_cep_filtrados[0] - 1

    # Passa por todos o espectro filtrado para verificar se o item atual faz parte de uma sequencia com o anterior
    for valor in espectro_cep_filtrados:

        # Se for uma sequencia do anterior, continua o intervalo
        if valor - 1 == anterior:
            anterior = valor

        # Se não for uma sequencia, fecha o intervalo e marca o anterior como fim do intervalo
        # Otual será o começo do proxima intervalo
        else:
            range_fim.append(anterior)
            range_inicio.append(valor)
            anterior = valor

    # Adiciona o último elemento como fim do ultimo intervalo
    range_fim.append(espectro_cep_filtrados[-1])

    # Retorna um dict para montar um dataframe
    return {'cep_inicial': range_inicio, 'cep_final': range_fim}


def get_region(range_cep: dict, conn: object):
    '''
    Retorna a região para os intervalos de CEPs
    :param range_cep: Dict com os range de CEPs
    :param conn: Conexão com o sqlite onde esta as tabelas com os range de cep de cada região.
    :return: DataFrame com os dados regionalizados
    '''

    # Monta um df para inserir no sqlite para pegar as regiões
    df_cep_sem_faixa = pd.DataFrame(range_cep)

    # inserir no sqlite para pegar as regiões
    df_cep_sem_faixa.to_sql('cep_gap', con=conn, if_exists='replace', index=False)

    # Query de consulta
    query = """
        SELECT 
            cg.cep_inicial,
            cg.cep_final,
            COALESCE(ci.macrorregiao, uf.macrorregiao) AS macrorregiao,
            COALESCE(ci.estado, uf.estado) AS estado,
            ci.mesoregiao,
            ci.microregiao,
            ci.cidade AS cidade_inicio,
            cf.cidade as cidade_final
        FROM cep_gap cg
        LEFT JOIN cidades ci 
            ON cg.cep_inicial  BETWEEN ci.cep_inicial AND ci.cep_final
        LEFT JOIN cidades cf 
            ON cg.cep_final  BETWEEN cf.cep_inicial AND cf.cep_final 
        LEFT JOIN estados uf
            ON cg.cep_inicial BETWEEN uf.cep_inicial AND uf.cep_final   
        ;
    """

    # DataFrame de retorno com os dados da consulta
    df = pd.read_sql(sql=query, con=con_db)

    # Retorna o DataFrame
    return df


if __name__ == '__main__':

    con_db = sqlite3.connect(config.ROOT_DIR + r'\files\regioes_ceps.db')

    # Intervalos de ceps
    df_ranges = pd.read_csv(config.ROOT_DIR + rf'\{config.NOME_CSV_ENTRADA}', encoding='utf-8-sig', delimiter=';')
    df_ranges.replace('-', '', regex=True, inplace=True)
    df_ranges = df_ranges.astype({'cep_inicial': int, 'cep_final': int})

    # Verifica o intervalor de CEP a ser analisados
    if config.AUTOMATICO_CSV:
        cep_inicio = config.CEP_INICIAL
        cep_final = config.CEP_FINAL
    else:
        cep_inicio = min(df_ranges['cep_inicial'])
        cep_final = max(df_ranges['cep_final'])

    # Converte para lista com elementos de tuplas, com um intervalo. Um parte de numeros com inicio e fim.
    df_ranges = list(df_ranges.to_records(index=False))

    # Chama a função para pegar as lacunas no espectro de ceps
    gap_ceps = cep_gap_finder(df_ranges, inicio_espectro=cep_inicio, fim_espectro=cep_final)

    # Localiza a região das lacunas
    gap_ceps = get_region(range_cep=gap_ceps, conn=con_db)

    # Salva em um CSV. 'utf-8-sig' Para o Excel abrir corretamente o arquivo.
    gap_ceps.to_csv(config.NOME_CSV_SAIDA, encoding='utf-8-sig', sep=';', index=False)
