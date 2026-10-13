"""
Module: loader.py
Responsible for loading the 10,000 record master original dataset
"""

import os
import pandas as pd

def load_master_10k(filepath):
    """
    Loads master 10,000 dataset without modifications.
    Preserves raw integrity and traceability.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Master dataset not found at: {filepath}")
    df = pd.read_csv(filepath, low_memory=False)
    return df
