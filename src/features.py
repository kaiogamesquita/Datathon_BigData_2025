import pandas as pd

def jan_2023_weeks(n_weeks: int = 4) -> pd.DataFrame:
    
    d = pd.date_range('2023-01-01','2023-01-31', freq='D')
    iso = d.isocalendar()
    tab = (pd.DataFrame({'ano_iso': iso.year, 'semana_iso': iso.week})
           .drop_duplicates()
           .sort_values(['ano_iso','semana_iso'])
           .head(n_weeks))
    tab['semana'] = range(1, len(tab)+1)
    return tab[['ano_iso','semana_iso','semana']]