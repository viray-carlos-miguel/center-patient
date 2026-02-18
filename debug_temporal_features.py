#!/usr/bin/env python3
"""
Debug temporal features: is_subacute should be included
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.data_processor import MedicalDataProcessor

def main():
    print("🔍 DEBUGGING TEMPORAL FEATURES")
    print("=" * 50)
    
    processor = MedicalDataProcessor()
    
    # Test extract_temporal_features
    temporal = processor.extract_temporal_features(72)  # 3 days = subacute
    print(f"extract_temporal_features(72) returns: {temporal}")
    print(f"Keys: {list(temporal.keys())}")
    print(f"Values: {list(temporal.values())}")
    
    # Test different durations
    for duration in [24, 72, 240]:  # acute, subacute, chronic
        temporal = processor.extract_temporal_features(duration)
        print(f"\nDuration {duration}h ({duration/24:.1f} days):")
        print(f"  {temporal}")

if __name__ == "__main__":
    main()
