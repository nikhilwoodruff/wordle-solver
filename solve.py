from typing import List, Tuple
import requests
from tqdm import tqdm

class Result:
    GREEN = "Green"
    YELLOW = "Yellow"
    BLACK = "Black"

class WordlePuzzle:
    def __init__(self, word: str = None):
        self.word = word

    def take_guess(self, guess: str):
        result = []
        if self.word is not None:
            for i in range(len(self.word)):
                if self.word[i] == guess[i]:
                    result += [Result.GREEN]
                elif guess[i] in self.word:
                    result += [Result.YELLOW]
                else:
                    result += [Result.BLACK]
        else:
            result = list(map(lambda x: {"g": Result.GREEN, "y": Result.YELLOW, "b": Result.BLACK}[x], input("Enter (b|y|g)+: ")))
        return result

CACHE = {}

class Wordle:
    max_attempts = 6
    trade_x_percent_win_chance_for_expected_step_faster = 1
    
    def __hash__(self):
        return hash(tuple(self.attempts))

    def __init__(self, attempts: List[str] = None, wordlist: List[str] = None):
        if attempts is None:
            self.attempts = []
        else:
            self.attempts = attempts
        if wordlist is None:
            self.wordlist = self._get_wordlist()
        else:
            self.wordlist = wordlist

        self.step_score_multiplier = self.trade_x_percent_win_chance_for_expected_step_faster / 100

    
    def _get_wordlist(self):
        words = requests.get("https://raw.githubusercontent.com/charlesreid1/five-letter-words/master/sgb-words.txt").content
        return words.decode("utf-8").split("\n")[:-1]

    @property
    def remaining_attempts(self):
        return self.max_attempts - len(self.attempts)
    
    def narrow(self, attempt: str, result: Tuple[str]):
        for i in range(len(attempt)):
            letter = attempt[i]
            colour = result[i]
            if colour == Result.BLACK:
                self.wordlist = list(filter(lambda word: letter not in word, self.wordlist))
            elif colour == Result.YELLOW:
                self.wordlist = list(filter(lambda word: (word[i] != letter) and (letter in word), self.wordlist))
            elif colour == Result.GREEN:
                self.wordlist = list(filter(lambda word: word[i] == letter, self.wordlist))
        
    def simulate_guess(self, guess: str, game: WordlePuzzle):
        attempt = Wordle(self.attempts + [guess], self.wordlist)
        result = game.take_guess(guess)
        attempt.narrow(guess, result)
        return attempt

    def best_guess(self, recursive: bool = False) -> str:
        if self in CACHE:
            return CACHE[self]
        if len(self.wordlist) == 1:
            return self.wordlist[0], 1
        if self.remaining_attempts == 1:
            # One guess left, just pick the first possible word
            best_guess = self.wordlist[0]
            win_chance = 1 / len(self.wordlist)
            num_attempts = self.max_attempts
            expected_score = win_chance - num_attempts * self.step_score_multiplier
            CACHE[self] = (best_guess, expected_score)
            return best_guess, expected_score
        else:
            # At least one guess after - simulate all possible puzzles
            expected_score_of_guess = {}
            wordlist = tqdm(self.wordlist, desc="Simulating guesses") if not recursive else self.wordlist
            for guess in wordlist:
                for answer in self.wordlist:
                    game = WordlePuzzle(answer)
                    # Take guess and narrow down
                    attempt = self.simulate_guess(guess, game)
                    _, expected_score = attempt.best_guess(recursive=True)
                    if guess not in expected_score_of_guess:
                        expected_score_of_guess[guess] = 0
                    expected_score_of_guess[guess] += expected_score / len(self.wordlist)
            best_guess, expected_score = max(expected_score_of_guess.items(), key=lambda x: x[1])
            CACHE[self] = (best_guess, expected_score)
            return best_guess, expected_score


    def __eq__(self, other):
        return (
            (len(self.attempts) == len(other.attempts))
            and all(map(lambda x: x[0] == x[1], zip(self.attempts, other.attempts)))
        )

def main():
    ai = Wordle()
    game = WordlePuzzle("rebus")
    ai = ai.simulate_guess("arose", game)
    while ai.remaining_attempts > 0:
        guess, expected_score = ai.best_guess()
        print(f"Guess: {guess} (exp. speed-adjusted score = {round(expected_score)})")
        ai = ai.simulate_guess(guess, game)

main()