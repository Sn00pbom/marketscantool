import pandas as pd
import numpy as np


class Rubric(object):

    def __init__(self, rubric_dict=None):
        self._rubric_dict = {} if rubric_dict is None else rubric_dict

    def __delitem__(self, key):
        del(self._rubric_dict[key])

    def __getitem__(self, key):
        return self._rubric_dict[key]

    def __setitem__(self, key, value):
        self._rubric_dict[key] = value

    def __str__(self):
        return str(self._rubric_dict)

    def __iter__(self):
        return iter(self._rubric_dict)

    def add_column(self, name, f, perfect, weight):
        self[name] = {'f': f, 'perfect': perfect, 'weight': weight}

    def keys(self):
        return [key for key in self]


class Grader(object):

    def __init__(self, rubric):
        self.rubric = rubric

    def _generate_score_sheet(self, data_dict):
        rubric = self.rubric
        score_sheet = pd.DataFrame([[rubric[col]['f'](data_dict, ticker) for col in rubric] for ticker in data_dict],
                                   columns=[col for col in rubric],
                                   index=[ticker for ticker in data_dict])
        return score_sheet

    def grade(self, data_dict) -> pd.DataFrame:
        score_sheet = self._generate_score_sheet(data_dict)
        score_sheet['Composite Score'] = np.sum(np.abs(score_sheet[col]) / self.rubric[col]['perfect']
                                                * self.rubric[col]['weight'] for col in score_sheet)
        return score_sheet
