import os
import argparse
import pandas as pd
import numpy as np

from .config import DATA_PATH, N_WEEKS_OUT
from .utils import log
from .data_io import map_files, weekly_aggregate_2022_stream
from .baselines import naive4_forecast, ewma_forecast
from .metrics import mae, rmse, mape, wmape


def unique_weeks_2022(wk: pd.DataFrame):
    
    weeks = wk[['ano_iso','semana_iso']].drop_duplicates().sort_values(['ano_iso','semana_iso'])
    weeks = weeks[(weeks['ano_iso'] == 2022) | (weeks['ano_iso'] == 2021)]  
    return list(map(tuple, weeks[['ano_iso','semana_iso']].itertuples(index=False, name=None)))

def make_calendar_from_weeks(test_weeks):
    cal = pd.DataFrame(test_weeks, columns=['ano_iso','semana_iso'])
    cal = cal.sort_values(['ano_iso','semana_iso']).reset_index(drop=True)
    cal['semana'] = np.arange(1, len(cal)+1, dtype=int)
    return cal[['ano_iso','semana_iso','semana']]

def filter_weeks(df, weeks_set):
    key = list(map(tuple, df[['ano_iso','semana_iso']].itertuples(index=False, name=None)))
    mask = [k in weeks_set for k in key]
    return df.loc[mask]


def rolling_origins(weeks_list, horizon=4, n_folds=6, min_train_weeks=16):
    """
    weeks_list: lista ordenada de (ano_iso, semana_iso) ao longo de 2022
    Retorna lista de folds: [(train_weeks_set, test_weeks_list), ...]
    """
    
    weeks = weeks_list
    
    start = min_train_weeks
    end = len(weeks) - horizon
    if end <= start:
        end = start + 1
   
    idxs = np.linspace(start, end-1, num=min(n_folds, max(1, end-start)), dtype=int)
    folds = []
    for o in idxs:
        train_weeks = set(weeks[:o+1])
        test_weeks = weeks[o+1:o+1+horizon]
        folds.append((train_weeks, test_weeks))
    return folds

def evaluate_baselines(horizon=4, n_folds=6, alpha=0.5, save_path=None):
    
    mapping = map_files(DATA_PATH)
    if 'transacoes' not in mapping:
        raise RuntimeError("Arquivo de transações não encontrado em data/.")

    wk = weekly_aggregate_2022_stream(mapping['transacoes'])
    
    wk = wk.sort_values(['pdv','produto','ano_iso','semana_iso'])

    weeks = unique_weeks_2022(wk)
    folds = rolling_origins(weeks, horizon=horizon, n_folds=n_folds, min_train_weeks=16)

    rows = []
    for i, (train_set, test_list) in enumerate(folds, start=1):
        log(f"Fold {i}/{len(folds)} | treino até {list(train_set)[-1]} | teste {test_list}")

        train_wk = filter_weeks(wk, train_set)
        test_wk  = filter_weeks(wk, set(test_list))

        
        cal = make_calendar_from_weeks(test_list)

        
        pred_naive = naive4_forecast(train_wk, cal)
        pred_ewma  = ewma_forecast(train_wk, cal, alpha=alpha)

        
        y_true = (test_wk
                  .merge(cal, on=['ano_iso','semana_iso'], how='inner')
                  [['semana','pdv','produto','quantidade']]
                  .rename(columns={'quantidade':'y'}))

       
        def score(pred, name):
            dfm = y_true.merge(pred, on=['semana','pdv','produto'], how='left', validate='one_to_one')
            dfm['quantidade'] = dfm['quantidade'].fillna(0).astype(int)
            m = {
                'fold': i,
                'model': name,
                'wmape': wmape(dfm['y'], dfm['quantidade']),
                'mape':  mape(dfm['y'], dfm['quantidade']),
                'mae':   mae(dfm['y'], dfm['quantidade']),
                'rmse':  rmse(dfm['y'], dfm['quantidade']),
                'n_rows': len(dfm)
            }
            return m

        rows.append(score(pred_naive, "naive4"))
        rows.append(score(pred_ewma,  f"ewma_a{alpha}"))

    res = pd.DataFrame(rows)
    res_overall = (res.groupby('model', as_index=False)
                     .agg({'wmape':'mean','mape':'mean','mae':'mean','rmse':'mean','n_rows':'sum'}))
    res_overall = res_overall.sort_values('wmape')

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        res.to_csv(save_path.replace(".csv", "_folds.csv"), index=False)
        res_overall.to_csv(save_path, index=False)

    return res, res_overall

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=N_WEEKS_OUT, help="4 ou 5 semanas")
    ap.add_argument("--folds", type=int, default=6, help="número de origens (folds) ao longo de 2022")
    ap.add_argument("--alpha", type=float, default=0.5, help="alpha do EWMA")
    ap.add_argument("--out", type=str, default="docs/validation_baselines.csv", help="onde salvar a tabela resumo")
    args = ap.parse_args()

    log("Iniciando avaliação local (backtesting 2022)")
    res_folds, res_overall = evaluate_baselines(horizon=args.horizon, n_folds=args.folds,
                                                alpha=args.alpha, save_path=args.out)
    log("Resultados por fold:")
    print(res_folds)
    log("Média por modelo (ordenado por WMAPE):")
    print(res_overall)

if __name__ == "__main__":
    main()