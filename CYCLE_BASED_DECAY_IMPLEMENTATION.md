# Cycle-Based Temporal Decay Implementation

## Summary

Successfully converted the temporal decay mechanism from wall-clock time to reasoning cycles. The system now decays edges based on usage patterns (number of reasoning cycles) rather than absolute time.

## Changes Made

### 1. Core Knowledge Graph (`core/knowledge_graph/knowledgeGraph.py`)

#### Relation Class
- **Changed**: `last_activated` → `cycles_since_last_activation`
- **Type**: `None` (never activated) or `int` (cycles since last use)
- **Backwards compatibility**: Automatically converts old `last_activated` timestamps to `cycles_since_last_activation=0` when loading old data

#### New Method: `increment_cycle_counters()`
```python
def increment_cycle_counters(self):
    """
    Increment the cycle counter for all edges that have been activated at least once.
    Should be called at the start of each reasoning cycle.
    """
    for rel in self.relations:
        if rel.cycles_since_last_activation is not None:
            rel.cycles_since_last_activation += 1
```

#### Updated Method: `activate_relation()`
- Now resets `cycles_since_last_activation = 0` when edge is used
- Removed datetime timestamp assignment

#### Updated Method: `apply_temporal_decay()`
- **Old formula**: `decay = gamma * (1 - exp(-days_inactive / 30))`
- **New formula**: `decay = gamma * (1 - exp(-cycles_inactive / 5))`
- Changed from 30-day half-life to 5-cycle characteristic length
- Removed all datetime operations

### 2. Orchestrator (`core/orchestrator/index.py`)

#### Updated: `apply_hebbian_learning()`
- Now calls `knowledge_graph.increment_cycle_counters()` at the start of each reasoning cycle
- This increments the inactivity counter for all previously-activated edges

### 3. Tests (`tests/test_hebbian_plasticity.py`)

#### Updated: `test_temporal_decay()`
- Changed from simulating days (`timedelta(days=60)`) to simulating cycles (`cycles_since_last_activation = 5`)
- Added mathematical verification of decay formula
- Verified expected decay: `0.05 * (1 - exp(-1)) ≈ 0.0316` absolute units

#### Updated: `test_memory_consolidation()`
- Changed from 180 days to 20 cycles of inactivity

#### Updated: `test_persistence_with_hebbian_data()`
- Changed assertion from `last_activated` to `cycles_since_last_activation`

### 4. Documentation

#### Paper (`paper.tex`)
- Updated formula from days to cycles
- Changed from 30-day half-life to 5-cycle characteristic length
- Added explanation: "an edge unused for 5 reasoning cycles decays identically whether those cycles occur over 1 day or 1 month"

#### README (`README.md`)
- Updated formula and parameters
- Added rationale explaining cycle-based approach
- Emphasized usage-pattern-based decay vs. wall-clock time

## Formula Details

### New Decay Formula
```
decay = γ × (1 - exp(-cycles_inactive / λ))
```

Where:
- `γ = 0.05` (decay rate)
- `λ = 5` (characteristic length in cycles)
- `cycles_inactive` = number of reasoning cycles since edge was last traversed

### Expected Decay After 5 Cycles
```
decay = 0.05 × (1 - exp(-5/5))
      = 0.05 × (1 - exp(-1))
      = 0.05 × (1 - 0.368)
      = 0.05 × 0.632
      ≈ 0.0316 absolute units
```

For typical edge strengths:
- Strength 0.3: decay = 10.5%
- Strength 0.4: decay = 7.9%
- Strength 0.5: decay = 6.3%
- Strength 0.6: decay = 5.3%

## Test Results

All tests passed successfully:

```
✅ Knowledge Graph operations
✅ Hebbian edge strengthening (LTP)
✅ Temporal decay (LTD) - Cycle-Based
✅ Emergent connection formation
✅ Memory consolidation
✅ Data persistence
```

### Cycle-Based Decay Test Output
```
Initial strength (after activation): 0.5500
After 5 cycles decay: 0.5184
Decay amount: 0.0316
Expected decay: 0.0316
✅ SUCCESS: Decay amount matches expected formula!
```

## Key Benefits

1. **Usage-Pattern Based**: Decay depends on reasoning activity, not wall-clock time
2. **Consistent Behavior**: 5 unused cycles produce the same decay whether they happen over 1 day or 1 month
3. **Deterministic**: No dependency on system clock or timestamps
4. **Testable**: Easy to simulate specific numbers of cycles in tests
5. **Biologically Inspired**: Mimics how memories fade with lack of use, not passage of time

## Implementation Notes

### Cycle Counter Management
1. At the start of each reasoning cycle, call `kg.increment_cycle_counters()`
2. When an edge is traversed, call `kg.activate_relation()` which resets its counter to 0
3. Edges never activated have `cycles_since_last_activation = None` and are excluded from decay

### Backwards Compatibility
- Loading old knowledge graphs with `last_activated` timestamps automatically converts them to `cycles_since_last_activation = 0`
- This assumes recently-loaded edges were "just used"

## Migration Path

To migrate existing knowledge graphs:
1. Load the old graph (automatic conversion happens)
2. Save immediately to persist in new format
3. All new reasoning cycles will use cycle-based decay

## Files Modified

1. `core/knowledge_graph/knowledgeGraph.py` - Core implementation
2. `core/orchestrator/index.py` - Cycle counter integration
3. `tests/test_hebbian_plasticity.py` - Updated tests
4. `paper.tex` - Updated documentation
5. `README.md` - Updated documentation
6. `scripts/test_cycle_based_decay.py` - New demonstration script (can be removed)

## Verification

Run the tests:
```bash
python tests/test_hebbian_plasticity.py
```

Run the cycle-based decay demonstration:
```bash
python scripts/test_cycle_based_decay.py
```

Both should show all tests passing with cycle-based decay working correctly.

