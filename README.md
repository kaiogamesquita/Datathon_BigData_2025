# Datathon Big Data 2025 - Forecast Challenge

Repositório desenvolvido para o **Hackathon Forecast Big Data 2025**, organizado pela Big Data.  
O desafio consiste em **prever a quantidade semanal de vendas por PDV/SKU para as quatro primeiras semanas de janeiro de 2023**, utilizando como base o histórico transacional do ano de 2022.

---

## 🎯 Objetivo

Construir uma solução de previsão que:
- Supere o baseline oficial da organização.
- Entregue resultados consistentes e reprodutíveis.
- Demonstre qualidade técnica e criatividade na abordagem.

----

## 📂 Estrutura do Repositório

- **data/** → instruções e dados de entrada (não versionados integralmente).  
- **notebooks/** → análises exploratórias, visualizações e prototipagem de modelos.  
- **src/** → código-fonte organizado (pipeline de dados, modelagem e validação).  
- **output/** → previsões geradas (`.csv` ou `.parquet`).  
- **docs/** → documentação complementar (gráficos, relatórios, diagramas).  

---

## ⚙️ Como rodar

1. Clone este repositório:
   ```bash
   git clone https://github.com/kaiogamesquita/Datathon_BigData_2025.git
   cd Datathon_BigData_2025

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt

3. Execute o pipeline principal:
   ```bash
   python src/train.py 

---
📊 Resultados esperados

Formato de entrega:
Semana | PDV | Produto | Quantidade
2023-01 | 001 | ABC123 | 57
2023-01 | 001 | XYZ987 | 12
...

---

👥 Autor
Kaio Gefferson de Almeida Mesquita
Doutorando em Engenharia de Transportes (UFC)
Foco em confiabilidade operacional, acessibilidade e inteligência artificial aplicada a transportes.



