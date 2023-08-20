from os import getcwd

# Diretorio root do projeto
ROOT_DIR = getcwd()

# Nomes dos arquivos csv usandos
NOME_CSV_ENTRADA = 'intervalos_ceps.csv'
NOME_CSV_SAIDA = 'gap_espectro_ceps.csv'

# Define se o incio e fim do espectro de CEPs analizados terá como base o menor e o maior valor do csv
AUTOMATICO_CSV = False

# Se False, usa as faixas abaixo, se True, usa as faixas do csv como paramentro
CEP_INICIAL = 1000000
CEP_FINAL = 99999999
