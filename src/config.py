import os

# raiz do repositório (…/Datathon_BigData_2025)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# permite sobrescrever via variável de ambiente, se quiser
DATA_PATH = os.getenv("BD_DATA_PATH", os.path.join(REPO_ROOT, "data"))

OUTPUT_DIR = os.getenv("BD_OUTPUT_DIR", os.path.join(REPO_ROOT, "output"))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "predictions.csv")

CSV_SEP = ";"
CSV_ENCODING = "utf-8"

N_WEEKS_OUT = int(os.getenv("BD_N_WEEKS_OUT", 4))  # troque para 5 se necessário
RANDOM_STATE = 42