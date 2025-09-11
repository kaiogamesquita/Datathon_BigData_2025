import numpy as np
import pandas as pd

def naive4_forecast(df_weekly: pd.DataFrame, cal_weeks: pd.DataFrame) -> pd.DataFrame:
    
    last4 = (df_weekly.sort_values(['pdv','produto','ano_iso','semana_iso'])
                      .groupby(['pdv','produto'])
                      .tail(4)
                      .groupby(['pdv','produto'], as_index=False)['quantidade']
                      .mean()
                      .rename(columns={'quantidade':'q_hat'}))

    rep = cal_weeks.copy(); rep['key']=1
    last4['key']=1
    out = last4.merge(rep, on='key').drop(columns='key')

    out['quantidade'] = np.clip(np.rint(out['q_hat']).astype('int64'), 0, None)
    return out[['semana','pdv','produto','quantidade']]

def ewma_forecast(df_weekly: pd.DataFrame, cal_weeks: pd.DataFrame, alpha: float = 0.5) -> pd.DataFrame:
    """
    Nível exponencial (EWMA) por série usando todo 2022; replica o último nível para as semanas de saída.
    """
    def last_level(g):
        lvl = g['quantidade'].ewm(alpha=alpha, adjust=False).mean().iloc[-1]
        return pd.Series({'q_hat': lvl})
    levels = df_weekly.groupby(['pdv','produto']).apply(last_level).reset_index()

    rep = cal_weeks.copy(); rep['key']=1
    levels['key']=1
    out = levels.merge(rep, on='key').drop(columns='key')

    out['quantidade'] = np.clip(np.rint(out['q_hat']).astype('int64'), 0, None)
    return out[['semana','pdv','produto','quantidade']]