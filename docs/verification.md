# Verification and demonstration

## Test scope

Expected values follow the project working guide and documented logic. The supplemental Python model checks abstract synchronous behavior, not IC propagation delays, electrical levels, PCB routing or manufacturing readiness. The source guide describes Proteus simulation and a reviewed recording, but the recording, editable simulation and measured hardware waveforms were not supplied in this repository snapshot.

## Integrated 0001 demonstration

1. Assert RESET_N=0 with LOAD=1. Check generator 0001, PISO 0000, AB=00 and DETECT=0.
2. Release reset during the low phase of the clock. Keep LOAD high for exactly one rising edge.
3. Check the captured PISO word is 0001; the generator has advanced to 0010.
4. During the next low phase, select LOAD=0. Observe the next four rising edges.

| Edge | Old X accepted | PISO after edge | AB | DETECT |
|---|---|---|---|---|
| Load | — | 0001 | 00 | 0 |
| 1 | 0 | 0010 | 01 | 0 |
| 2 | 0 | 0100 | 10 | 0 |
| 3 | 0 | 1000 | 11 | 0 |
| 4 | 1 | 0000 | 00 | 1 |

With an uninterrupted clock, DETECT returns low on the next edge. Select LOAD again before a fifth shift if the goal is word-based testing. Additional shifts produce zeros even when no generated data remains. Additional load edges overwrite the captured word.

The source guide uses a 0.1 Hz simulation clock for slow manual observation. The table is based on logical signal values, not indicator drive polarity.

## Expected test cases

Start each independent test from AB=00. For arbitrary streams, use a controlled simulation input or arrange captures to produce the required stream; the LFSR does not support direct arbitrary word selection.

| ID | Test | Expected result |
|---|---|---|
| T01 | Reset | Generator 0001; all other stored state cleared |
| T02 | LFSR full cycle | All 15 nonzero states, then seed repeats |
| T03 | Capture and serialize 0001 | Pulse on fourth shift |
| T04 | 0101, 1000, 1111 | No match in first four accepted bits |
| T05 | 0000 (reset-empty PISO) | AB=11 after three shifts; no detection |
| T06 | 00001 | Pulse on fifth bit |
| T07 | 00010001 | Pulses on accepted bits 4 and 8 |
| T08 | 1010, load interval, then 0010 | FSM holds prefix during load; match on seventh accepted bit |
| T09 | LOAD=1 over multiple clocks | PISO repeatedly captures; FSM holds; DETECT clears |
| T10 | One load and four shifts, repeated | Three distinct sampled words per fixed-phase cycle |

## Run the supplemental model tests

From repository root, with Python 3 (standard library only):

```bash
python -m unittest discover -s verification -v
python verification/model.py
```

The tests cover the logical equations and do not claim successful Proteus or physical-board verification. Record actual observations separately.

## Evidence to add

- Proteus project file and a screenshot of the complete simulation.
- Actual timing capture of CLK, RESET_N, LOAD, X, A, B, DETECT and ideally both parallel words.
- Test log comparing expected versus observed results, including failed tests and fixes.
- Physical prototype photos and measured waveforms, if built and tested.
- Editable EasyEDA project, ERC/DRC report and Gerbers only after manufacturing review.

## Known behavior

A reset-empty PISO can contribute zeros to the serial stream, so a later one may legitimately trigger detection without a captured word of 0001. Demonstrate the complete word capture and four shifts to distinguish an end-to-end test from a detector-only test. LOAD does not reset the FSM, so partial matches can continue across words.
