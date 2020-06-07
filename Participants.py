
from accessify import private
from accessify import protected
import numpy as np



class tailler:

    def __init__(self):
        self._my_shares = {} # election : (shares_sum)

    def recive_shares(self, election, shares):
        sum_of_shares = np.empty(np.shape(shares[0]))
        for share in shares:
            sum_of_shares += share
        
        try:
            self._my_shares[election] += sum_of_shares
        except:
            self._my_shares[election] = sum_of_shares

class voter:   
    
    def __init__(self):
        self._ballots = {} # election : ballot np.shape((candidates_number))
        self._ballots_shares = {} # election : ballot_shares np.shape((taillers_number, candidates_number))

    @protected
    def _send_ballots(self, election):
        return self._ballots[election]

    @protected
    def _send_shares(self, election):
        return self._ballots_shares[election]

    @protected
    def _cast_ballot(self, election, get_input):
        new_ballot = get_input(election)
        self._ballots[election] = new_ballot

    @protected
    def _secret_sharing_generation(self, election, random_gen):
        
        input_ballot = self._ballots[election]
        taillers_number = len(election.taillers)
        ballot_elem_field = election.ballot_elem_field

        candidates_number = len(input_ballot)   

        assert np.shape(input_ballot) != (candidates_number), \
        "input_ballot must be a numpy array of (candidates_number) instead of " + type(input_ballot) 

        new_ballot_shares = np.zeros((taillers_number, candidates_number))

        for D in range(taillers_number - 1):
            for C in range(candidates_number):
                new_ballot_shares[D][C] = random_gen(0, ballot_elem_field)

        ballot_shares_sum = np.sum(new_ballot_shares, axis = 0) % ballot_elem_field
        new_ballot_shares[len(new_ballot_shares) - 1] = ballot_shares_sum


        self._ballots_shares[election] = new_ballot_shares

        return new_ballot_shares





    
