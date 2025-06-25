"""
Auto-generated digital life form
Generation: 1
Lineage: 831fd0a7
DNA: {
  "behavior": "defensive",
  "metabolism": "fast",
  "reproduction": "mitosis",
  "resilience": 0.2083401014991958,
  "mutation_rate": 0.07479972531459922,
  "lifespan": 62
}
"""

from src.evolution.digital_life import SelfReplicatingCell, DigitalDNA

# This cell's DNA
dna = DigitalDNA({"behavior": "defensive", "metabolism": "fast", "reproduction": "mitosis", "resilience": 0.2083401014991958, "mutation_rate": 0.07479972531459922, "lifespan": 62})

# Instantiate this cell
cell = SelfReplicatingCell(dna=dna)

if __name__ == "__main__":
    print(f"Cell {cell.id} is alive!")
    print(f"Behavior: {cell.dna.genes['behavior']}")
    print(f"Generation: {cell.dna.generation}")
