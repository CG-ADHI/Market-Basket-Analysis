"""
Market Basket Analysis - Rules Engine
======================================
This script performs association rule mining on transactional data
using Apriori and FP-Growth algorithms, and outputs rules sorted by Lift.
"""

import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import time
import warnings
warnings.filterwarnings('ignore')


def load_and_preprocess_data(csv_path):
    """
    Load transactional data and convert from long format to one-hot encoded matrix.

    Args:
        csv_path: Path to the transactions CSV file

    Returns:
        tuple: (one_hot_df, original_df, transactions_list)
    """
    print("=" * 60)
    print("STEP 1: DATA LOADING & PREPROCESSING")
    print("=" * 60)

    # Load raw data
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} transaction records")
    print(f"Unique transactions: {df['TransactionID'].nunique()}")
    print(f"Unique products: {df['Item'].nunique()}")

    # Show top 10 best-selling items
    top_items = df['Item'].value_counts().head(10)
    print("\nTop 10 Best-Selling Items:")
    for item, count in top_items.items():
        print(f"  {item}: {count}")

    # Convert to list of lists (basket format)
    transactions = df.groupby('TransactionID')['Item'].apply(list).tolist()
    print(f"\nTotal baskets: {len(transactions)}")

    # One-hot encoding using TransactionEncoder
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    one_hot_df = pd.DataFrame(te_ary, columns=te.columns_)

    print(f"\nOne-hot encoded matrix shape: {one_hot_df.shape}")
    print(f"Density: {one_hot_df.values.sum() / (one_hot_df.shape[0] * one_hot_df.shape[1]):.4f}")

    return one_hot_df, df, transactions


def generate_frequent_itemsets_apriori(one_hot_df, min_support=0.02):
    """
    Generate frequent itemsets using the Apriori algorithm.

    Args:
        one_hot_df: One-hot encoded transaction matrix
        min_support: Minimum support threshold

    Returns:
        DataFrame of frequent itemsets with support values
    """
    print("\n" + "=" * 60)
    print("STEP 2A: FREQUENT ITEMSETS - APRIORI ALGORITHM")
    print("=" * 60)

    start_time = time.time()
    frequent_itemsets = apriori(one_hot_df, min_support=min_support, use_colnames=True, verbose=1)
    apriori_time = time.time() - start_time

    print(f"\nApriori execution time: {apriori_time:.4f} seconds")
    print(f"Number of frequent itemsets found: {len(frequent_itemsets)}")

    if len(frequent_itemsets) > 0:
        print("\nTop 10 Frequent Itemsets (by support):")
        top_itemsets = frequent_itemsets.nlargest(10, 'support')
        for idx, row in top_itemsets.iterrows():
            items = ', '.join(list(row['itemsets']))
            print(f"  {items}: Support = {row['support']:.4f}")

    return frequent_itemsets, apriori_time


def generate_frequent_itemsets_fpgrowth(one_hot_df, min_support=0.02):
    """
    Generate frequent itemsets using the FP-Growth algorithm.

    Args:
        one_hot_df: One-hot encoded transaction matrix
        min_support: Minimum support threshold

    Returns:
        DataFrame of frequent itemsets with support values
    """
    print("\n" + "=" * 60)
    print("STEP 2B: FREQUENT ITEMSETS - FP-GROWTH ALGORITHM")
    print("=" * 60)

    start_time = time.time()
    frequent_itemsets = fpgrowth(one_hot_df, min_support=min_support, use_colnames=True, verbose=1)
    fpgrowth_time = time.time() - start_time

    print(f"\nFP-Growth execution time: {fpgrowth_time:.4f} seconds")
    print(f"Number of frequent itemsets found: {len(frequent_itemsets)}")

    if len(frequent_itemsets) > 0:
        print("\nTop 10 Frequent Itemsets (by support):")
        top_itemsets = frequent_itemsets.nlargest(10, 'support')
        for idx, row in top_itemsets.iterrows():
            items = ', '.join(list(row['itemsets']))
            print(f"  {items}: Support = {row['support']:.4f}")

    return frequent_itemsets, fpgrowth_time


def generate_association_rules(frequent_itemsets, min_confidence=0.6, min_lift=1.2):
    """
    Generate association rules from frequent itemsets and filter by confidence and lift.

    Args:
        frequent_itemsets: DataFrame of frequent itemsets
        min_confidence: Minimum confidence threshold
        min_lift: Minimum lift threshold

    Returns:
        DataFrame of filtered association rules sorted by lift
    """
    print("\n" + "=" * 60)
    print("STEP 3: ASSOCIATION RULE GENERATION & FILTERING")
    print("=" * 60)

    # Generate all rules
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    print(f"\nTotal rules generated (confidence >= {min_confidence}): {len(rules)}")

    # Filter by lift
    rules_filtered = rules[rules['lift'] >= min_lift].copy()
    print(f"Rules after lift filter (lift >= {min_lift}): {len(rules_filtered)}")

    # Sort by lift descending
    rules_sorted = rules_filtered.sort_values('lift', ascending=False).reset_index(drop=True)

    # Add readable antecedents and consequents
    rules_sorted['antecedents_str'] = rules_sorted['antecedents'].apply(lambda x: ', '.join(list(x)))
    rules_sorted['consequents_str'] = rules_sorted['consequents'].apply(lambda x: ', '.join(list(x)))

    # Select and reorder columns for output
    output_cols = ['antecedents_str', 'consequents_str', 'support', 'confidence', 'lift', 'leverage', 'conviction']
    rules_output = rules_sorted[output_cols].copy()
    rules_output.columns = ['Antecedent (If)', 'Consequent (Then)', 'Support', 'Confidence', 'Lift', 'Leverage', 'Conviction']

    return rules_output


def compare_algorithms(apriori_time, fpgrowth_time, apriori_itemsets, fpgrowth_itemsets):
    """Compare Apriori and FP-Growth performance."""
    print("\n" + "=" * 60)
    print("STEP 4: ALGORITHM COMPARISON")
    print("=" * 60)

    print(f"\nApriori Time:  {apriori_time:.4f} seconds")
    print(f"FP-Growth Time: {fpgrowth_time:.4f} seconds")

    if apriori_time > 0:
        speedup = apriori_time / fpgrowth_time if fpgrowth_time > 0 else float('inf')
        print(f"FP-Growth is {speedup:.2f}x {'faster' if speedup > 1 else 'slower'} than Apriori")

    print(f"\nApriori Itemsets:  {len(apriori_itemsets)}")
    print(f"FP-Growth Itemsets: {len(fpgrowth_itemsets)}")


def save_rules_to_csv(rules_df, output_path='association_rules.csv'):
    """Save association rules to CSV."""
    rules_df.to_csv(output_path, index=False)
    print(f"\nRules saved to {output_path}")
    print(f"Total rules exported: {len(rules_df)}")


def print_top_rules(rules_df, n=20):
    """Print top N rules in a formatted table."""
    print("\n" + "=" * 60)
    print(f"TOP {n} ASSOCIATION RULES (Sorted by Lift)")
    print("=" * 60)

    if len(rules_df) == 0:
        print("No rules found matching the criteria.")
        return

    display_df = rules_df.head(n).copy()
    display_df['Support'] = display_df['Support'].apply(lambda x: f"{x:.4f}")
    display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.4f}")
    display_df['Lift'] = display_df['Lift'].apply(lambda x: f"{x:.4f}")
    display_df['Leverage'] = display_df['Leverage'].apply(lambda x: f"{x:.4f}")
    display_df['Conviction'] = display_df['Conviction'].apply(lambda x: f"{x:.4f}" if not np.isinf(x) else "inf")

    pd.set_option('display.max_colwidth', 40)
    pd.set_option('display.width', 200)
    print(display_df.to_string(index=False))


def main():
    """Main execution pipeline."""
    print("\n" + "#" * 60)
    print("# MARKET BASKET ANALYSIS - RULES ENGINE")
    print("#" * 60)

    # Configuration
    CSV_PATH = 'transactions.csv'
    MIN_SUPPORT = 0.02
    MIN_CONFIDENCE = 0.6
    MIN_LIFT = 1.2

    # Step 1: Load and preprocess data
    one_hot_df, original_df, transactions = load_and_preprocess_data(CSV_PATH)

    # Step 2: Generate frequent itemsets using both algorithms
    apriori_itemsets, apriori_time = generate_frequent_itemsets_apriori(one_hot_df, MIN_SUPPORT)
    fpgrowth_itemsets, fpgrowth_time = generate_frequent_itemsets_fpgrowth(one_hot_df, MIN_SUPPORT)

    # Step 3: Compare algorithms
    compare_algorithms(apriori_time, fpgrowth_time, apriori_itemsets, fpgrowth_itemsets)

    # Step 4: Generate association rules (using FP-Growth itemsets as they're typically more complete)
    rules_df = generate_association_rules(fpgrowth_itemsets, MIN_CONFIDENCE, MIN_LIFT)

    # Step 5: Display and save results
    print_top_rules(rules_df, n=20)
    save_rules_to_csv(rules_df, 'association_rules.csv')

    print("\n" + "#" * 60)
    print("# PIPELINE COMPLETE")
    print("#" * 60)

    return rules_df


if __name__ == "__main__":
    rules = main()