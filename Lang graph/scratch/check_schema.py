from schema import PARAMETER_KEYS, VALIDATION_RULES
print(f"Parameters: {len(PARAMETER_KEYS)}")
print(f"Composite: {sum(1 for r in VALIDATION_RULES.values() if r['is_composite'])}")
print(f"Atomic: {sum(1 for r in VALIDATION_RULES.values() if not r['is_composite'])}")
print(f"First: {PARAMETER_KEYS[0]}")
print(f"Last: {PARAMETER_KEYS[-1]}")
