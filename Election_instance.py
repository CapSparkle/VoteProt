
from enum import Enum
import copy

class voting_rules(Enum):
    PLURALITY = 1
    RANGE = 2
    APPROVAL = 3
    VETO = 4
    BORDA = 5

class candidate:
    def __init__(self, name, order_in_ballot):
        self.__name = name
        self.__order_in_ballot = order_in_ballot

    @property
    def name(self):
        return self.__name

    @property
    def order_in_ballot(self):
        return self.__order_in_ballot


class election:
    __uid_counter = -1

    def __init__(self, candidates = [], taillers = [], voters = [], e_voting_rules = voting_rules.PLURALITY, winners_number_sought = 1, ballot_elem_field = 4294967294):
        election.__uid_counter +=1
        self._uid = election.__uid_counter
        
        for candidate in candidates:
            index_pool = []
            [index_pool.append(i) for i in range(len(candidates))]

            if candidate.order_in_ballot in index_pool:
                index_pool.pop(candidate.order_in_ballot)
            else:
                raise ValueError('incorrect candidates indexing')

        self._candidates = candidates
        self._taillers = taillers
        self._voters = voters

        self._voting_rules = e_voting_rules

        assert winners_number_sought <= len(candidates)
        self._winners_number_sought = winners_number_sought 

        self._ballot_elem_field = ballot_elem_field

    @property
    def uid(self):
        return self._uid

    @property
    def candidates(self):
        return self._candidates

    @property
    def taillers(self):
        return self._taillers

    @property
    def voters(self):
        return self._voters

    @property
    def voting_rules(self):
        return self._voting_rules

    @property
    def winners_number_sought(self):
        return self._winners_number_sought

    @property
    def ballot_elem_field(self):
        return self._ballot_elem_field