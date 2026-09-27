from pathlib import Path
import csv, json, math
from collections import Counter
from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'transactions.csv'
RULES = ROOT / 'outputs' / 'association_rules.csv'
app = Flask(__name__)

def parse_items(value):
    if value is None:
        return []
    value = str(value).strip()
    value = value.strip('{}[]()')
    return [x.strip().strip("'\"") for x in value.split(',') if x.strip()]

def load_data():
    transactions = []
    if DATA.exists():
        with DATA.open(newline='', encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))
        # Support common column names in the supplied dataset.
        by_tx = {}
        for row in rows:
            tx = row.get('TransactionID') or row.get('Transaction ID') or row.get('transaction_id') or row.get('InvoiceNo') or row.get('id')
            item = row.get('Item') or row.get('Product') or row.get('product') or row.get('Description') or row.get('item')
            if tx is not None and item:
                by_tx.setdefault(str(tx), set()).add(item.strip())
        transactions = list(by_tx.values())

    rules = []
    if RULES.exists():
        with RULES.open(newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                rules.append({
                    'antecedent': row.get('Antecedent (If)', ''),
                    'consequent': row.get('Consequent (Then)', ''),
                    'support': float(row.get('Support') or 0),
                    'confidence': float(row.get('Confidence') or 0),
                    'lift': float(row.get('Lift') or 0),
                    'leverage': float(row.get('Leverage') or 0),
                    'conviction': row.get('Conviction', ''),
                })
    counts = Counter(item for basket in transactions for item in basket)
    return transactions, rules, counts

def summary_payload():
    transactions, rules, counts = load_data()
    products = len(counts)
    top_items = [{'name': n, 'count': c} for n, c in counts.most_common(8)]
    top_rules = sorted(rules, key=lambda x: (x['lift'], x['confidence']), reverse=True)
    return {
        'metrics': {
            'transactions': len(transactions),
            'products': products,
            'rules': len(rules),
            'high_value_rules': sum(1 for r in rules if r['lift'] >= 2 and r['confidence'] >= .6),
        },
        'top_items': top_items,
        'rules': top_rules,
        'clusters': [
            {'name': 'Breakfast & Dairy', 'items': ['Milk', 'Bread', 'Butter', 'Cereal', 'Bananas', 'Yogurt', 'Granola']},
            {'name': 'Personal Care', 'items': ['Shampoo', 'Conditioner', 'Body Wash', 'Toothpaste']},
            {'name': 'Cooking Essentials', 'items': ['Pasta', 'Ground Beef', 'Tomato Sauce', 'Cheese']},
            {'name': 'Meal Ingredients', 'items': ['Rice', 'Chicken', 'Vegetables', 'Sauce']},
        ]
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summary')
def api_summary():
    return jsonify(summary_payload())

@app.route('/api/recommend')
def api_recommend():
    product = request.args.get('product', '').strip().lower()
    payload = summary_payload()
    matches = []
    for rule in payload['rules']:
        if product and product in rule['antecedent'].lower():
            matches.append(rule)
    return jsonify({'product': product, 'recommendations': matches[:12]})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
