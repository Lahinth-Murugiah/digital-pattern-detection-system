import unittest
from model import System, fsm_next, lfsr_next


class DigitalSystemTests(unittest.TestCase):
    def test_reset(self):
        s = System(15, 15, 3, 1)
        s.tick(False, reset_n=False)
        self.assertEqual((s.rng, s.piso, s.state, s.detect), (1, 0, 0, 0))

    def test_lfsr_cycle(self):
        word = 1
        seen = []
        for _ in range(15):
            seen.append(word)
            word = lfsr_next(word)
        self.assertEqual(seen, [1, 2, 4, 9, 3, 6, 13, 10, 5, 11, 7, 15, 14, 12, 8])
        self.assertEqual(word, 1)
        self.assertEqual(lfsr_next(0), 0)

    def test_integrated_word(self):
        s = System()
        self.assertIsNone(s.tick(True))
        self.assertEqual((s.rng, s.piso, s.state), (2, 1, 0))
        for bit, piso, state, detect in [(0, 2, 1, 0), (0, 4, 2, 0), (0, 8, 3, 0), (1, 0, 0, 1)]:
            self.assertEqual(s.tick(False), bit)
            self.assertEqual((s.piso, s.state, s.detect), (piso, state, detect))
        s.tick(True)
        self.assertEqual(s.detect, 0)

    def test_streams(self):
        for stream, expected in [('0101', []), ('1000', []), ('1111', []), ('0000', []), ('00001', [5]), ('00010001', [4, 8])]:
            with self.subTest(stream=stream):
                state = 0
                hits = []
                for i, bit in enumerate(stream, 1):
                    state, detect = fsm_next(state, int(bit))
                    if detect:
                        hits.append(i)
                self.assertEqual(hits, expected)

    def test_cross_word(self):
        state = 0
        for bit in '1010':
            state, detect = fsm_next(state, int(bit))
            self.assertEqual(detect, 0)
        self.assertEqual((state, detect), (1, 0))
        state, detect = fsm_next(state, 1, load=True)
        self.assertEqual((state, detect), (1, 0))
        for bit in '001':
            state, detect = fsm_next(state, int(bit))
        self.assertEqual((state, detect), (0, 1))

    def test_empty_piso(self):
        s = System()
        for _ in range(10):
            self.assertEqual(s.tick(False), 0)
            self.assertEqual(s.detect, 0)
        self.assertEqual(s.state, 3)

    def test_repeated_load(self):
        s = System(state=2, detect=1)
        for word in [1, 2, 4]:
            s.tick(True)
            self.assertEqual((s.piso, s.state, s.detect), (word, 2, 0))

    def test_fixed_sampling(self):
        s = System()
        words = []
        for _ in range(6):
            s.tick(True)
            words.append(s.piso)
            for _ in range(4):
                s.tick(False)
        self.assertEqual(words[:3], words[3:])
        self.assertEqual(len(set(words)), 3)

    def test_all_states_and_inputs(self):
        for state in range(4):
            for bit in (0, 1):
                expected = (0, int(state == 3)) if bit else (min(state + 1, 3), 0)
                self.assertEqual(fsm_next(state, bit), expected)
                self.assertEqual(fsm_next(state, bit, load=True), (state, 0))


if __name__ == '__main__':
    unittest.main()
