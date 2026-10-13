import os
import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset"

# Load MaintIE gold and silver to extract entity vocabularies
maintie_gold_path = os.path.join(base, "maintie-main", "data", "gold_release.json")
with open(maintie_gold_path, 'r', encoding='utf-8') as f:
    gold = json.load(f)

print(f"MaintIE gold records: {len(gold)}")

# Collect terms by entity type
actions = set()
components = set()
states = set()

for item in gold:
    tokens = item.get('tokens', [])
    for ent in item.get('entities', []):
        etype = ent.get('type', '')
        start = ent.get('start', 0)
        end = ent.get('end', 0)
        phrase = " ".join(tokens[start:end]).lower()
        if 'Activity' in etype or 'Action' in etype:
            actions.add(phrase)
        elif 'PhysicalObject' in etype:
            components.add(phrase)
        elif 'State' in etype:
            states.add(phrase)

print(f"Discovered Actions: {len(actions)} sample: {list(actions)[:10]}")
print(f"Discovered Components: {len(components)} sample: {list(components)[:10]}")
print(f"Discovered States/Failures: {len(states)} sample: {list(states)[:10]}")

# Parse MaintNorm records
def parse_maintnorm_file(filepath):
    records = []
    current_id = None
    tokens_raw = []
    tokens_norm = []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                if current_id and tokens_norm:
                    records.append({
                        'record_id': current_id,
                        'text_raw': " ".join(tokens_raw),
                        'text_norm': " ".join(tokens_norm)
                    })
                current_id = None
                tokens_raw = []
                tokens_norm = []
                continue
            
            parts = line_str.split('\t')
            if len(parts) == 2:
                raw_t, norm_t = parts
                if norm_t == '<id>':
                    current_id = raw_t
                else:
                    tokens_raw.append(raw_t)
                    tokens_norm.append(norm_t)
        if current_id and tokens_norm:
            records.append({
                'record_id': current_id,
                'text_raw': " ".join(tokens_raw),
                'text_norm': " ".join(tokens_norm)
            })
    return records

maintnorm_train = os.path.join(base, "maintnorm-main", "data", "combined", "train.norm")
train_recs = parse_maintnorm_file(maintnorm_train)
print(f"Parsed {len(train_recs)} records from train.norm")
print("First 3 records:")
for r in train_recs[:3]:
    print(" ", r)
