# Market Basket Analysis for Upselling and Cross-Selling

## Objective
Discover products that are frequently purchased together using association rule mining.
The results support bundle offers, cross-selling, product placement, checkout
recommendations, and business strategy planning.

## Structure
- `data/transactions.csv` - raw transaction data
- `src/rules_engine.py` - preprocessing, Apriori, FP-Growth, and rule generation
- `src/network_visualization.py` - network graph, interactive HTML, and cluster heatmap
- `src/strategy_proposal.py` - business strategy PDF generator
- `outputs/` - generated results and visualizations
- `docs/Project_Requirements.pdf` - original project requirements
- `requirements.txt` - Python dependencies
- `run_all.py` - end-to-end runner

## Installation
Install Python 3.9+ and run:

```bash
pip install -r requirements.txt
```

## Run the complete project
From the project root:

```bash
python run_all.py
```

The runner stages the input CSV for the existing scripts, executes the rules engine,
visualization pipeline, and strategy proposal generator, then copies the newest
artifacts into `outputs/`.

## Parameters
- Minimum support: `0.02`
- Minimum confidence: `0.60`
- Minimum lift: `1.20`

## Metrics
- **Support:** proportion of transactions containing an itemset.
- **Confidence:** probability of buying the consequent when the antecedent is purchased.
- **Lift:** confidence divided by the consequent's support. Lift greater than 1 indicates
  a positive association relative to independence.

## Outputs
- `association_rules.csv`
- `network_graph.png`
- `network_interactive.html`
- `cluster_analysis.png`
- `Business_Strategy_Proposal.pdf`

## Limitation
The supplied dataset is small, so very high lift or confidence values may be sensitive
to individual transactions. Validate recommendations with a larger dataset or A/B test
before production deployment.
