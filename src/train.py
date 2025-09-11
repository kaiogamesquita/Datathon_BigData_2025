import os
import argparse
import pandas as pd

from .config import N_WEEKS_OUT, DATA_PATH, OUTPUT_PATH, CSV_SEP, CSV_ENCODING
from .utils import log, ensure_dir
from .data_io import map_files, weekly_aggregate_2022_stream
from .features import jan_2023_weeks
#from .baselines import naive4_forecast  
from .baselines import ewma_forecast

def run(n_weeks_out: int = N_WEEKS_OUT, out_path: str = OUTPUT_PATH):
    log("Iniciando pipeline")

   
    mapping = map_files(DATA_PATH)
    if 'transacoes' not in mapping:
        raise RuntimeError("Arquivo de TRANSAÇÕES não encontrado em data/. Verifique os .parquet.")

    trans_path = mapping['transacoes']
    log(f"Usando transações: {os.path.basename(trans_path)}")

    
    log("Agregando vendas semanais de 2022...")
    wk = weekly_aggregate_2022_stream(trans_path)
    log(f"Semanas agregadas: {wk.shape}")

    
    cal = jan_2023_weeks(n_weeks=n_weeks_out)

   
    log("Gerando baseline EWMA...")
    pred = ewma_forecast(wk, cal, alpha=0.5)

    
    pred = pred[['semana','pdv','produto','quantidade']].copy()
    ensure_dir(out_path)
    pred.to_csv(out_path, sep=CSV_SEP, index=False, encoding=CSV_ENCODING)
    log(f"Arquivo gerado em: {out_path} | linhas: {len(pred)}")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--weeks", type=int, default=N_WEEKS_OUT, help="Número de semanas (4 ou 5)")
    p.add_argument("--out", type=str, default=OUTPUT_PATH, help="Caminho do CSV de saída")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run(n_weeks_out=args.weeks, out_path=args.out)