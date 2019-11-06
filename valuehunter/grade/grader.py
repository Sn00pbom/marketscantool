import pandas as pd
import numpy as np

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
        rubrick = self.rubrick
        score_sheet = self._generate_score_sheet(data_dict)
        score_sheet['Composite Score'] = np.sum(np.abs(score_sheet[col]) / rubrick[col]['perfect'] * rubrick[col]['weight'] for col in score_sheet)
        return score_sheet
