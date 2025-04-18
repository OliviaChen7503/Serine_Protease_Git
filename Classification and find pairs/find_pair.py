import pandas as pd
import numpy as np
from datetime import datetime  # NEW: For timestamp

# ========================
# STEP 1: Load and categorize data
# ========================
def load_and_categorize_data(csv_file):
    df = pd.read_csv(csv_file)
    
    # Clean up the "Resolution (A)" column and convert to numeric
    # NEW: Handle non-numeric values (e.g., "no_Jg") and rename column
    df = df.rename(columns={"Resolution (Å)": "Resolution"})  # Fix column name if needed
    df["Resolution"] = pd.to_numeric(df["Resolution"], errors="coerce")  # Convert to NaN for invalid entries
    
    # Clean up the "State" column
    df["State"] = df["State"].str.extract(r'(APO|GSA-bound|TSA-bound)', expand=False)
    
    # Drop rows with invalid resolution or state
    df = df.dropna(subset=["State", "Resolution"])
    
    # Split into categories
    apo = df[df["State"] == "APO"]
    gsa = df[df["State"] == "GSA-bound"]
    tsa = df[df["State"] == "TSA-bound"]
    
    return apo, gsa, tsa

# ========================
# STEP 2: Pair-finding logic
# ========================
def find_pairs(group1, group2, name1, name2):
    pairs = []
    
    for idx1, row1 in group1.iterrows():
        # Filter by SpaceGroup first
        matches = group2[group2["SpaceGroup"] == row1["SpaceGroup"]]
        
        for idx2, row2 in matches.iterrows():
            # Check unit cell lengths
            length_diff = np.abs(row1[["UnitCell_L1", "UnitCell_L2", "UnitCell_L3"]] - 
                           row2[["UnitCell_L1", "UnitCell_L2", "UnitCell_L3"]])
            
            # Check unit cell angles
            angle_diff = np.abs(row1[["UnitCell_A1", "UnitCell_A2", "UnitCell_A3"]] - 
                          row2[["UnitCell_A1", "UnitCell_A2", "UnitCell_A3"]])
            
            # NEW: Check resolution difference
            resolution_diff = abs(row1["Resolution"] - row2["Resolution"])
            
            if (
                (length_diff.max() < 1.0) and 
                (angle_diff.max() < 0.1) and 
                (resolution_diff < 0.2)  # NEW criterion
            ):
                pairs.append((row1["PDB ID"], row2["PDB ID"]))
    
    return {f"{name1}_vs_{name2}": pairs}

# ========================
# MAIN EXECUTION
# ========================
if __name__ == "__main__":
    apo, gsa, tsa = load_and_categorize_data("Serine_Protease_Suppmentary_table - Elastase(filtered).csv")  # Replace with your CSV path
    
    results = {}
    results.update(find_pairs(apo, gsa, "APO", "GSA"))
    results.update(find_pairs(apo, tsa, "APO", "TSA"))
    results.update(find_pairs(gsa, tsa, "GSA", "TSA"))

    # NEW: Save results to a file
    output_file = f"pair_results_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    
    with open(output_file, "w") as f:
        f.write("=== Comparable PDB Pairs ===\n")
        for comparison, pairs in results.items():
            f.write(f"\n{comparison} pairs ({len(pairs)} found):\n")
            for pair in pairs:
                f.write(f"{pair[0]} <-> {pair[1]}\n")
    
    print(f"\nResults saved to: {output_file}")
