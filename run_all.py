"""Run the complete Market Basket Analysis pipeline end-to-end."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)

# Existing scripts expect transactions.csv and generated files in their own folder.
shutil.copy2(DATA / "transactions.csv", SRC / "transactions.csv")

steps = [
    SRC / "rules_engine.py",
    SRC / "network_visualization.py",
    SRC / "strategy_proposal.py",
]

for script in steps:
    print("\n" + "=" * 70)
    print("Running:", script.name)
    print("=" * 70)
    subprocess.run([sys.executable, str(script)], cwd=SRC, check=True)

# Copy the newest generated artifacts to the organized outputs directory.
artifact_names = [
    "association_rules.csv",
    "network_graph.png",
    "network_interactive.html",
    "cluster_analysis.png",
    "Business_Strategy_Proposal.pdf",
]
for name in artifact_names:
    generated = SRC / name
    if generated.exists():
        shutil.copy2(generated, OUTPUTS / name)

print("\nPipeline completed successfully.")
print("Updated files are available in the outputs/ directory.")
