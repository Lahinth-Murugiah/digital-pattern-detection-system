"""Supplemental clock-edge behavioral model of the documented logic.
Not an original Proteus circuit, netlist, or physical timing simulation.
"""
from dataclasses import dataclass


def lfsr_next(word: int) -> int:
    feedback = ((word >> 3) ^ (word >> 2)) & 1
    return ((word << 1) & 0xF) | feedback


def fsm_next(state: int, bit: int, load: bool = False) -> tuple[int, int]:
    if load:
        return state, 0
    a, b = (state >> 1) & 1, state & 1
    nx = 1 - bit
    next_a = nx & (a | b)
    next_b = nx & (a | (1 - b))
    return (next_a << 1) | next_b, a & b & bit


@dataclass
class System:
    rng: int = 1
    piso: int = 0
    state: int = 0
    detect: int = 0

    def reset(self) -> None:
        self.rng, self.piso, self.state, self.detect = 1, 0, 0, 0

    def tick(self, load: bool, reset_n: bool = True) -> int | None:
        if not reset_n:
            self.reset()
            return None
        old_rng, old_piso = self.rng, self.piso
        bit = (old_piso >> 3) & 1
        self.state, self.detect = fsm_next(self.state, bit, load)
        self.piso = old_rng if load else (old_piso << 1) & 0xF
        self.rng = lfsr_next(old_rng)
        return None if load else bit


if __name__ == '__main__':
    system = System()
    print('event     X    RNG   PISO  AB   DETECT')
    for label, load in [('load', True)] + [(f'shift {i}', False) for i in range(1, 5)]:
        bit = system.tick(load)
        print(f'{label:9} {str(bit):4} {system.rng:04b}  {system.piso:04b}  {system.state:02b}   {system.detect}')
