from Participants import voter, tailler
from Election_instance import election, voting_rules, candidate

import numpy as np
import random

from mpyc.runtime import mpc


class lab_voter(voter):
    
    def take_part_in_elections(self, election, get_input, random_gen, send_shares_by_myself = False):
        self._cast_ballot(election, get_input)
        
        if send_shares_by_myself:
            self._secret_sharing_generation(election, random_gen)

            shares_list = self._send_shares(election)
            for tailler, share in zip(election.taillers, shares_list):
                tailler.recive_shares(election, share)

    def send_ballots(self, election):
        return self._send_ballots(election)

class lab_tailler(tailler):
    
    def take_part_in_elections(self, election):
        pass

    def send_shares(self, election):
        return self._my_shares[election]


class DT_lab_elections:

    def __init__(self):
        self.secint = mpc.SecInt()

    def Perform_simple_lab_elections_1(self, election, special_input = None, regular_input_method = None, random_gen = None):
        if random_gen == None:
            random_gen = random.randint
        if regular_input_method == None:
            regular_input_method = self.Make_random_ballot

        #___Ballot Casting & (Sending & Tailler precompututaiton Phase___) (1, 2, (3, 4) steps):
        
        voters_i = 0
        if special_input:
            for input_method, number in special_input.items():
                for j in range(number):
                    if voters_i >= len(election.voters):
                        break
                    
                    election.voters[voters_i].take_part_in_elections(election, input_method, random_gen)
                    voters_i += 1

        while voters_i < len(election.voters):
            election.voters[voters_i].take_part_in_elections(election, regular_input_method, random_gen)
            voters_i += 1


        #___MPC step ((3,4), 5 steps) :

        result = mpc.run(self._main_MPC(election))
        print(result)


        #___Publishing Phase___ (6 step):

        if result == "illegal ballot by voter":
            return

        for win_indicator, candidate_index in zip(result, range(len(Candidates))):
            if win_indicator:
                for candidate in Candidates:
                    if candidate.order_in_ballot == candidate_index:
                        print(f'{candidate.name} is won elections №{election.uid}')




    def Make_random_ballot(self, election, ignore_rules = False):
        candidate_number = len(election.candidates)
        
        if ignore_rules:
            return
        
        ballot = np.zeros((candidate_number))
        if election.voting_rules == voting_rules.PLURALITY:
            ballot[random.randint(0, len(election.candidates) - 1)] = 1
        
        return ballot


    async def _main_MPC(self, election, validate_ballots = True):
        

        async with mpc:
            
        #___emulating ballots sharing +++ABSOLUTELY SECURE+++
        # and aggregated scores of all candidates evaluating:
            candidates_number = len(election.candidates)
            secret_shared_ballots = []
            ordered_aggregated_scores = [mpc.input(self.secint(0 if mpc.pid == 0 else None), senders = 0)] * candidates_number

            for voters_i in range(len(election.voters)):
                secret_shared_ballots.append([])

                ballot = election.voters[voters_i].send_ballots(election)
                for value, candidate_index in zip(ballot, range(len(ballot))):
                    secint_value = mpc.input(self.secint((int(value)) if mpc.pid == 0 else None), senders = 0)
                    secret_shared_ballots[voters_i].append(secint_value)
                    
                    ordered_aggregated_scores[candidate_index] += secint_value

        #___MPC ballots validating:
                if validate_ballots:
                    ballot_is_valid = await self._ballot_validation(secret_shared_ballots[voters_i], election.voting_rules)
                    if not ballot_is_valid:
                        print(f'stop right there, voter number {voters_i}! You violating the law!')
                        return "illegal ballot by voter"

        #___MPC magic of top K candidates finding:
            comparsions_vector = [mpc.input(self.secint(0 if mpc.pid == 0 else None), senders = 0)] * candidates_number

            for candidate_i_scores, candidate_index in zip(ordered_aggregated_scores, range(candidates_number)):
                for candidate_j_scores in ordered_aggregated_scores:
                    comparsions_vector[candidate_index] += (candidate_i_scores > candidate_j_scores)

            for candidate_index in range(candidates_number):
                comparsions_vector[candidate_index] = (comparsions_vector[candidate_index] >= (candidates_number - election.winners_number_sought))

            elections_result = []
            for win_indicator in comparsions_vector:
                elections_result.append(await mpc.output(win_indicator))
            
            return elections_result 


    async def _ballot_validation(self, ballot, voting_rules):
        if voting_rules == voting_rules.PLURALITY:
            ballotsum = self.secint(0)

            for value in ballot:
                ballotsum += value
                if await mpc.output((value - self.secint(1)) * value) != 0:
                    return False

            out_ballotsum = await mpc.output(ballotsum)
            if out_ballotsum != 1:
                return False
            
            return True



def illegal_ballot_caster(election):
    if election.voting_rules == voting_rules.PLURALITY:
        return np.array([0, 0, -1])

if __name__ == "__main__":

    Candidates = [candidate("Vladimir Putin the 'Molodec!'", 0), candidate("Vladimir Jirinovsky the 'Jirik'", 1), candidate("Alexey Navalny the 'blat'", 2), candidate("Evegeniy Ponasenkov the 'Geniy!'", 3)]
    Taillers = [lab_tailler() for i in range(5)] 
    Voters = [lab_voter() for i in range(100)]
    
    Election = election(Candidates, Taillers, Voters, winners_number_sought= 1)

    
    Lab_elec = DT_lab_elections()
    Lab_elec.Perform_simple_lab_elections_1(Election)
    #special_input = {illegal_ballot_caster: 1}