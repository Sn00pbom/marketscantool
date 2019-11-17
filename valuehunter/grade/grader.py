import pandas as pd
import numpy as np

class Rubrick(object):

    def __init__(self, rubrick_dict=None):
        self._rubrick_dict = {} if rubrick_dict is None else rubrick_dict

    def __delitem__(self, key):
        del(self._rubrick_dict[key])

    def __getitem__(self, key):
        return self._rubrick_dict[key]

    def __setitem__(self, key, value):
        self._rubrick_dict[key] = value

    def __str__(self):
        return str(self._rubrick_dict)

    def __iter__(self):
        return iter(self._rubrick_dict)

    def add_column(self, name, f, perfect, weight):
        self[name] = {'f':f,'perfect':perfect,'weight':weight}

    def keys(self):
        return [key for key in self]


class Grader(object):

    def __init__(self, rubrick):
        self.rubrick = rubrick

    def _generate_score_sheet(self, data_dict):
        rubrick = self.rubrick
        score_sheet = pd.DataFrame([[rubrick[col]['f'](data_dict, ticker) for col in rubrick] for ticker in data_dict],
                                columns=[col for col in rubrick],
                                index=[ticker for ticker in data_dict])
        return score_sheet

    def grade(self, data_dict) -> pd.DataFrame:
        score_sheet = self._generate_score_sheet(data_dict)
        score_sheet['Composite Score'] = np.sum(np.abs(score_sheet[col]) / self.rubrick[col]['perfect'] * self.rubrick[col]['weight'] for col in score_sheet)
        return score_sheet