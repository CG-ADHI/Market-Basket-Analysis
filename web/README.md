# BasketIQ Company Dashboard

This is the company-style web frontend for the Market Basket Analysis project.

## Start the website

From the project root, with the virtual environment activated:

```powershell
python -m pip install -r requirements.txt
python web/app.py
```

Open this address in your browser:

```text
http://127.0.0.1:5000
```

The dashboard reads the generated `outputs/association_rules.csv` and the transaction data in `data/transactions.csv`.
