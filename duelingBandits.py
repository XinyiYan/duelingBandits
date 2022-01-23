from collections import defaultdict
import math
import random
import argparse
import numpy as np
from collections import Counter


class RoundEfficient:
    def __init__(self, delta, pref_matrix, T):
        self.T = T
        self.delta = delta
        self.pref_matrix = pref_matrix
        self.n = len(pref_matrix)
        self.arms = set(range(self.n))
        self.t = 0
        self.competitions = 0
        self.totalScores = defaultdict(int)
        self.identicalCompare = defaultdict(int)


    def scaledScore(self, St):
        nt = len(self.arms)
        if nt % 2 == 0:
            r = 2 * (nt - 1) / nt 
        else:
            r = 2
        return r * St


    def Ct(self):
        return math.sqrt( 18 / self.t * math.log(2 * self.n * self.t ** 2 / self.delta))

    def prune(self):
        implausibleArms = set()
        bestScore = max(self.totalScores.values())
        Ct = self.Ct()

        for arm in self.arms:
            if self.totalScores[arm] < bestScore - self.t * Ct:
                implausibleArms.add(arm)

        for arm in implausibleArms:
            self.arms.remove(arm)
            self.totalScores.pop(arm, None)


    def oneRoundDueling(self):
        self.t += 1
        remainingArms = self.arms.copy()
        pairsTobeJudged = set()

        #generate pairs
        while len(remainingArms) > 1:
            pair = random.sample(remainingArms, 2)
            pairsTobeJudged.add(tuple(pair))
            remainingArms.remove(pair[0])
            remainingArms.remove(pair[1])

        #make judgments
        for pair in pairsTobeJudged:
            self.competitions += 1
            if random.random() <= self.pref_matrix[pair[0]][pair[1]]:
                preferred = pair[0]
            else:
                preferred = pair[1]
            self.totalScores[preferred] += self.scaledScore(1)
            self.identicalCompare[tuple(sorted(pair))] += 1

            if self.competitions > self.T:
                break

        #prune
        self.prune()

    def dueling(self):
        while len(self.arms) > 1 and self.competitions < self.T:
            self.oneRoundDueling()

        max_val = max(self.totalScores.values())
        return max(self.identicalCompare.values()), [k for k, v in self.totalScores.items() if v == max_val], self.competitions


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run_file",
        default=None,
        type=str,
        required=True,
        help="The file containing preference matrix.",
    )

    parser.add_argument(
        "--delta",
        default=0.2,
        type=float,
        required=False,
        help="the allowed error probability.",
    )

    parser.add_argument(
        "--T",
        default=1000000,
        type=int,
        required=False,
        help="the maximum time steps.",
    )

    parser.add_argument(
        "--iterations",
        default=1,
        type=int,
        required=False,
        help="",
    )

    args = parser.parse_args()
    pref_matrix = np.loadtxt(args.run_file)

    copeland_score = (pref_matrix > 0.5).sum(
        axis=1) / float(len(pref_matrix) - 1)

    winners = np.argwhere(copeland_score == np.amax(copeland_score)).flatten()
    print("winners: ", winners)
    print("num of arms: ", len(pref_matrix))

    steps = []
    topArmsLen = []
    identical_compares = []    

    winnersFound = [0] * len(winners)

    for _ in range(args.iterations):
        duelingBandits = RoundEfficient(args.delta, pref_matrix[:], args.T)
        max_identical_compare, topArms, steps_taken = duelingBandits.dueling()

        steps.append(steps_taken)
        topArmsLen.append(len(topArms))
        identical_compares.append(max_identical_compare)

        correct_arms = 0
        for arm in topArms:
            if arm in winners:
                correct_arms += 1

        if correct_arms != 0:
            winnersFound[correct_arms-1] += 1

    for idx, found in enumerate(winnersFound):
        if found:
            print('find ' + str(idx+1) + ' winner(s) ' + str(found) + ' times.')

    print('max_identical_compare', min(identical_compares),max(identical_compares))
    print('total comparisons', min(steps), max(steps))

    print("(key, value) -> Return key arms value times.", Counter(topArmsLen))

    



        
            

            

















