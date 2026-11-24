# Technical design

## Signals and clocking

`R3..R0` (also named `RNG3..RNG0` in the PCB schematic) are the generator word; `Q3..Q0` are the PISO word; `X = Q3`; `A,B` are FSM state bits. Let `L = LOAD`, `S = SHIFT = NOT L`. `DETECT` is the logical registered output (called OUTPUT in the working guide). All 11 active flip-flops share the same rising-edge clock. Reset is active-low and asynchronous.

| RESET_N | LOAD | Generator | PISO | FSM | DETECT |
|---|---|---|---|---|---|
| 0 | either | 0001 | 0000 | 00 | 0 |
| 1 | 1 | Advance | Capture old generator word | Hold | 0 after edge |
| 1 | 0 | Advance | Shift, zero fill | Accept old Q3 | Register match |

Every expression below uses pre-edge values. The prime suffix denotes the next stored value; `·` is AND, `+` is OR, `¬` is NOT.

## LFSR

```text
R0' = R3 XOR R2
R1' = R0
R2' = R1
R3' = R2
```

The reset seed 0001 produces a 15-state cycle; 0000 is an absorbing state. The system advances on both LOAD and SHIFT edges.

## PISO

```text
Q0' = L·R0
Q1' = L·R1 + S·Q0
Q2' = L·R2 + S·Q1
Q3' = L·R3 + S·Q2
```

The AND/OR network selects either the parallel inputs or the preceding register stages. Q0 receives zero during shifting. A captured word is serialized in the order R3, R2, R1, R0.

## FSM design and Boolean minimization

| AB | Interpretation | X=0: next AB / match | X=1: next AB / match |
|---|---|---|---|
| 00 | No prefix | 01 / 0 | 00 / 0 |
| 01 | One trailing zero | 10 / 0 | 00 / 0 |
| 10 | Two trailing zeros | 11 / 0 | 00 / 0 |
| 11 | At least three trailing zeros | 11 / 0 | 00 / 1 |

Karnaugh maps for the shift-only functions, derived from the transition table. Column order is Gray code. Match M is combinational; the final detection is registered.

| F_A | AB=00 | 01 | 11 | 10 |
|---|---:|---:|---:|---:|
| X=0 | 0 | 1 | 1 | 1 |
| X=1 | 0 | 0 | 0 | 0 |

Group 01/11 and 11/10: `F_A = ¬X·(A+B)`.

| F_B | AB=00 | 01 | 11 | 10 |
|---|---:|---:|---:|---:|
| X=0 | 1 | 0 | 1 | 1 |
| X=1 | 0 | 0 | 0 | 0 |

Group 11/10 and the wraparound pair 10/00: `F_B = ¬X·(A+¬B)`.

| M | AB=00 | 01 | 11 | 10 |
|---|---:|---:|---:|---:|
| X=0 | 0 | 0 | 0 | 0 |
| X=1 | 0 | 0 | 1 | 0 |

The isolated 1 gives `M = A·B·X`.

The complete mode-qualified equations are:

```text
A' = L·A + S·¬X·(A+B)
B' = L·B + S·¬X·(A+¬B)
DETECT' = S·A·B·X
```

The state can already be 00 when DETECT is high, because the output stores the match computed from the previous state. The FSM recognizes a serial suffix, not exclusively a word aligned to a PISO load boundary.

## EasyEDA PCB schematic reference mapping

The working guide describes a Proteus/netlist reference numbering scheme; the EasyEDA schematic uses different designators. Use the following mapping for the uploaded PCB export, not the guide's simulation IC numbers.

| Signal / function | EasyEDA reference | Q pin |
|---|---|---:|
| A | U1:A | 5 |
| B | U1:B | 9 |
| Q0 | U2:A | 5 |
| Q1 | U2:B | 9 |
| Q2 | U3:A | 5 |
| Q3 / X | U3:B | 9 |
| DETECT | U4:A | 5 |
| RNG0 | U4:B | 9 |
| RNG1 | U5:A | 5 |
| RNG2 | U5:B | 9 |
| RNG3 | U6:A | 5 |
| Unused flip-flop | U6:B | — |

U7–U10: 74LS08; U11–U12: 74LS32; U13: 74LS04; U14: 74LS86. U14:A provides XOR feedback. The output LED is connected through an inverter in the PCB schematic; logical DETECT is the non-inverted U4:A Q signal. The LED indicators are drawn with current supplied through resistors from +5 V, so confirm their sink-drive polarity rather than assuming the LED net is active-high.

The uploaded schematic is a raster export, not an editable netlist; this reference mapping is a visual inspection and is not an electrical connectivity or ERC sign-off.

## Physical implementation review

The visible PCB has top and bottom copper layers, through-hole components, 12 indicators, separate supply and clock terminals, reset and LOAD controls. Before ordering a board, verify footprints, clearances, copper widths, power and ground distribution, clock integrity, switch conditioning and logic-level/current requirements. The drawing shows a single 47 µF supply capacitor; local 100 nF bypass capacitors at each IC are a recommended improvement, not a feature shown in the supplied schematic. Confirm that all unused logic inputs have defined levels. Use the native CAD project to perform ERC/DRC and export manufacturing files.
