#!/usr/bin/env python3
"""
Este script Lê DBF do Sinan e os prepara para exportar para outro SGBD
Como Usar:
$ ./load_sinan.py <arquivo dbf do sinan> <YYYY>
"""

import pandas as pd
import psycopg2
from datetime import datetime, date
from psycopg2.extras import DictCursor
from dbfread import DBF
import logging
import sys
from decouple import config

db_config = {
    'database': config('POSTGRES_DATABASE'),
    'user': config('POSTGRES_USER'),
    'password': config('POSTGRES_PASSWORD'),
    'host': config('POSTGRES_HOST'),
    'port': config('POSTGRES_PORT'),
}

logger = logging.getLogger('Load_SINAN')

field_map = {
    'dt_notific': "DT_NOTIFIC",
    'se_notif': "SEM_NOT",
    'ano_notif': "NU_ANO",
    'dt_sin_pri': "DT_SIN_PRI",
    'se_sin_pri': "SEM_PRI",
    'dt_digita': "DT_DIGITA",
    'bairro_nome': "NM_BAIRRO",
    'bairro_bairro_id': "ID_BAIRRO",
    'municipio_geocodigo': "ID_MUNICIP",
    'nu_notific': "NU_NOTIFIC",
    'cid10_codigo': "ID_AGRAVO",

}

def calculate_digit(dig):
    """
    Calcula o digito verificador do geocódigo de município
    :param dig: geocódigo com 6 dígitos
    :return: dígito verificador
    """
    peso = [1, 2, 1, 2, 1, 2, 0]
    soma = 0
    dig = str(dig)
    for i in range(6):
        valor = int(dig[i]) * peso[i]
        soma += sum([int(d) for d in str(valor)]) if valor > 9 else valor
    dv = 0 if soma % 10 == 0 else (10-(soma % 10))
    return dv

def add_dv(geocodigo):
    if len(str(geocodigo)) == 7:
        return geocodigo
    else:
        return int(str(geocodigo)+str(calculate_digit(geocodigo)))

class Sinan:
    """
    Introspecta arquivo DBF do SINAN preparando-o para inserção em outro banco.
    """
    def __init__(self, dbf_fname, ano, encoding="iso=8859-1"):
        """
        Instancia Objeto SINAN carregando-o a partir do arquivo indicado
        :param dbf_fname: Nome do arquivo dbf do Sinan
        :param ano: Ano dos dados
        :return:
        """
        self.ano = ano
        self.dbf = DBF(dbf_fname, encoding=encoding)
        self.colunas_entrada = self.dbf.field_names
        self.tabela = pd.DataFrame(list(self.dbf))
        self.tabela.drop_duplicates('NU_NOTIFIC', keep='first', inplace=True)
        self.geocodigos = self.tabela.ID_MUNICIP.dropna().unique()
        self._parse_date_cols()
        if not self.time_span[0].year == self.ano and self.time_span[1].year == self.ano:
            logger.error("O Banco contém notificações incompatíveis com o ano declarado!")

    def _parse_date_cols(self):
        print("Formatando as datas...")
        for col in filter(lambda x: x.startswith("DT"), self.tabela.columns):
            self.tabela[col] = pd.to_datetime(self.tabela[col], coerce=True)

    @property
    def time_span(self):
        """
        Escopo temporal do banco
        :return: (data_inicio, data_fim)
        """
        data_inicio = self.tabela['DT_NOTIFIC'].min()
        data_fim = self.tabela['DT_NOTIFIC'].max()
        return data_inicio, data_fim

    def save_to_pgsql(self, connection, table_name='"Municipio"."Notificacao"'):
        print("Escrevendo no PostgreSQL...")
        ano = self.time_span[1].year if self.time_span[0] == self.time_span[1] else self.ano
        geoclist_sql = ",".join([str(gc) for gc in self.geocodigos])
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("delete FROM {} where ano_notif={} and municipio_geocodigo in ({});".format(table_name, ano, geoclist_sql))
            cursor.execute("select * from {} limit 1;".format(table_name))
            col_names = [c.name for c in cursor.description if c.name != "id"]
            df_names = [field_map[n] for n in col_names]
            insert_sql = 'INSERT INTO {}({}) VALUES ({})'.format(table_name, ','.join(col_names), ','.join(['%s' for i in col_names]))
            for row in self.tabela[df_names].iterrows():
                row = row[1]
                row[0] = date.fromordinal(row[0].to_datetime().toordinal())
                row[1] = int(row[1][-2:])
                row[2] = int(row[2])
                row[3] = date.fromordinal(row[3].to_datetime().toordinal())
                row[4] = int(row[4][-2:])
                row[5] = None if isinstance(row[5], pd.tslib.NaTType) else date.fromordinal(row[5].to_datetime().toordinal())
                row[7] = None if not row[7] else int(row[7])
                row[8] = add_dv(int(row[8]))
                row[9] = int(row[9])

                cursor.execute(insert_sql, row)


            connection.commit()

if __name__ == "__main__":
    fname = sys.argv[1]
    ano = sys.argv[2]
    conn = psycopg2.connect(**db_config)
    S = Sinan(fname, ano)
    S.save_to_pgsql(conn)







