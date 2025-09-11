import os
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
from .utils import log


def list_parquets(data_path: str):
    return [f for f in os.listdir(data_path) if f.endswith(".parquet")]

def identify_kind(parquet_path: str) -> str:
    
    sch = pq.read_schema(parquet_path)
    cols = set(sch.names)

    # transações (nomes encontrados no seu preview)
    if {'transaction_date','internal_store_id','internal_product_id','quantity'}.issubset(cols):
        return 'transacoes'

    # dimensões
    if {'pdv','zipcode'}.issubset(cols) or {'pdv','categoria_pdv'}.issubset(cols):
        return 'dim_pdv'

    if {'internal_product_id','category'}.issubset(cols) or {'product','categoria'}.issubset(cols):
        return 'dim_produto'

    return 'desconhecido'

def map_files(data_path: str):
    files = list_parquets(data_path)
    mapping = {}
    for f in files:
        full = os.path.join(data_path, f)
        kind = identify_kind(full)
        mapping[kind] = full
        log(f"Arquivo detectado: {f}  =>  {kind}")
    return mapping


def weekly_aggregate_2022_stream(trans_path: str, batch_rows: int = 2_000_000):
   
    pf = pq.ParquetFile(trans_path)
    use_cols = ['transaction_date','internal_store_id','internal_product_id','quantity','net_value']
    parts = []

    for batch in pf.iter_batches(batch_size=batch_rows, columns=use_cols):
        df = batch.to_pandas(types_mapper=pd.ArrowDtype)  # economiza RAM
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df_2022 = df[df['transaction_date'].dt.year == 2022].copy()

        iso = df_2022['transaction_date'].dt.isocalendar()
        df_2022['ano_iso'] = iso.year.astype('int16')
        df_2022['semana_iso'] = iso.week.astype('int16')

        g = (df_2022
             .groupby(['internal_store_id','internal_product_id','ano_iso','semana_iso'], as_index=False)
             .agg(quantity=('quantity','sum'),
                  faturamento=('net_value','sum')))

        parts.append(g)

    out = (pd.concat(parts, ignore_index=True)
             .groupby(['internal_store_id','internal_product_id','ano_iso','semana_iso'], as_index=False)
             .sum())

    # padroniza nomes
    out = out.rename(columns={
        'internal_store_id':'pdv',
        'internal_product_id':'produto',
        'quantity':'quantidade'
    })
    return out


def read_dim_pdv(path: str, cols=None):
    cols = cols or ['pdv','premise','categoria_pdv','zipcode']
    return pd.read_parquet(path, columns=[c for c in cols if c in pq.read_schema(path).names])

def read_dim_produto(path: str, cols=None):
    # ajustar conforme cols existentes: 'internal_product_id','category','description', 'attr1'...'attr4'
    base = pq.read_schema(path).names
    if cols is None:
        cols = [c for c in ['internal_product_id','category','description','attr1','attr2','attr3','attr4'] if c in base]
    return pd.read_parquet(path, columns=cols)