import argparse
import pandas as pd
import numpy as np
import os

EXPECTED_COLUMNS = ["semana","pdv","produto","quantidade"]

def validate_submission(path, max_weeks=5, sep=";"):
    if not os.path.exists(path):
        return False, f"Arquivo não encontrado: {path}"

    try:
        df = pd.read_csv(path, sep=sep, dtype={'semana':int,'pdv':np.int64,'produto':np.int64,'quantidade':int})
    except Exception as e:
        return False, f"Falha ao ler CSV com separador '{sep}': {e}"

    
    if list(df.columns) != EXPECTED_COLUMNS:
        return False, f"Colunas inesperadas: {list(df.columns)}. Esperado: {EXPECTED_COLUMNS}"

    
    if (df[["semana","pdv","produto","quantidade"]].isna().any().any()):
        return False, "Há valores ausentes (NaN)."

    if not ((df["semana"] >= 1) & (df["semana"] <= max_weeks)).all():
        return False, f"Valores inválidos em 'semana' (fora de 1..{max_weeks})."

    if not (df["quantidade"] >= 0).all():
        return False, "Existem quantidades negativas."

    
    dups = df.duplicated(subset=["semana","pdv","produto"]).sum()
    if dups > 0:
        return False, f"Há {dups} linhas duplicadas para a chave (semana,pdv,produto)."

    
    sample = df.sample(min(5, len(df)), random_state=42)
    ok_msg = f"OK: {len(df)} linhas | semanas {df['semana'].min()}..{df['semana'].max()} | " \
             f"PDVs {df['pdv'].nunique()} | Produtos {df['produto'].nunique()}.\n\nAmostra:\n{sample}"
    return True, ok_msg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=str, required=True, help="caminho do CSV de submissão")
    ap.add_argument("--weeks", type=int, default=4, help="máximo de semanas (4 ou 5)")
    ap.add_argument("--sep", type=str, default=";", help="separador (padrão ';')")
    args = ap.parse_args()

    ok, msg = validate_submission(args.file, max_weeks=args.weeks, sep=args.sep)
    print(msg)
    if not ok:
        raise SystemExit(1)

if __name__ == "__main__":
    main()