# Wordle Solver

`solve.py` solves Wordle puzzles. It aims to maximise the probability of success, but you can adjust this to aim for speed with extra risk of failure: the parameter `trade_x_percent_win_chance_for_expected_step_faster` controls this. The full 6 attempts are just a bit out of the exponential zone for my computer (estimated time 14 hours to solve the first guess), but if you give it an initial guess it runs within seconds, and seems to solve all the time.
