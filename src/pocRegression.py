import pickle
import pathlib
import os
import pandas as pd
from typing import Dict
from enum import Enum

PFREF_COL_NAMES = ['Rk', 'Player', 'Tm', 'FantPos', 'Age', 'G', 'GS', 'PassCmp', 'PassAtt', 'PassYds',
                    'PassTD', 'PassInt', 'RushAtt', 'RushYds', 'RushY/A', 'RushTD', 'RecTgt', 'Rec', 'RecYds', 'RecY/R',
                    'RecTD', 'Fmb', 'FL', 'TD', '2PM', '2PP', 'FantPt', 'PPR', 'DKPt', 'FDPt',
                    'VBD', 'PosRank', 'OvRank', 'Year']
    
class ScoringType(Enum):
    PPR = 1
    HPPR = 0.5
    NPPR = 0

    def description(self):
        return 'Pts_' + self.name

class PointsConverter():
    def __init__(self, scoringType : ScoringType = ScoringType.NPPR):
        self.scoringType = scoringType
        self.score_dict = {'PassYds' : 0.04,
                            'PassTD' : 4,
                            'PassInt' : -2,
                            'RushYds' : 0.1,
                            'RushTD' : 6,
                            'Rec': self.scoringType.value,
                            'RecYds' : 0.1,
                            'RecTD' : 6,
                            'FL' : -2,
                            '2PM' : 2,
                            '2PP' : 2}

    def _score_row(self, row):
        sum = 0.0
        for cat, score in self.score_dict.items():
            addval = float(row[cat]) * score
            sum += addval
        return sum

    def prep_pts_df(self, 
                    fpts_dict : Dict[str, pd.DataFrame], 
                    pfref_colNames : Dict[str, str] = PFREF_COL_NAMES):
        # 1. Concatenate, rename cols, drop filler rows, reset index
        df = pd.concat(fpts_dict.values())
        df.columns = pfref_colNames    
        df = df.drop(df[df['Player'] == 'Player'].index) 
        df = df.reset_index().drop(['index','Rk'], axis = 1)    
        
        # 2. Convert numerics, fill nas with 0, then score
        score_cols = list(self.score_dict.keys()) + ['FantPt', 'PPR']
        df[score_cols] = df[score_cols].apply(pd.to_numeric)
        score_dict2 = {k : 0 for (k, v) in self.score_dict.items()}
        df.fillna(score_dict2, inplace=True)
        
        # 3. Score
        col_name = self.scoringType.description()
        df[col_name] = df.apply(self._score_row, axis = 1)
        if col_name == 'Pts_PPR':
            assert len(df[(df['Pts_PPR'] - df['PPR']) > 0.1]) == 0

        # 4. Clean player names of '*' and '+'
        df['Player'] = df['Player'].str.replace('[\*\+]', '', regex=True).str.strip()

        # 5. Limit to guys with positions, everyone without position has 0 or less pts scored
        df = df[df['FantPos'].notnull()].copy()
        return df

# pts_df = prep_pts_df(fpts_dict, pfref_colNames, score_dict)
# pts_df.head()
def merge_adp_dataset(pts_df_reg, adp_df):
    # i. Update player names for merge
    adp_df.loc[adp_df['Name'] == 'Robbie Anderson', 'Name'] = 'Chosen Anderson'
    adp_df.loc[adp_df['Name'] == 'Travis Etienne Jr.', 'Name'] = 'Travis Etienne'
    adp_df.loc[adp_df['Name'] == 'Joshua Palmer', 'Name'] = 'Josh Palmer'
    adp_df.loc[adp_df['Name'] == 'Jeff Wilson Jr.', 'Name'] = 'Jeff Wilson'
    adp_df.loc[adp_df['Name'] == 'J.J. Nelson', 'Name'] = 'JJ Nelson'
    adp_df.loc[(adp_df['Name'] == 'Cordarrelle Patterson') & (adp_df['Year'] < 2021), 'Position'] = 'WR'
    adp_df.loc[(adp_df['Name'] == 'Ty Montgomery') & (adp_df['Year'] .isin([2016, 2017, 2018])), 'Position'] = 'RB'
    adp_df.loc[adp_df['Name'] == 'Brian Robinson', 'Name'] = 'Brian Robinson Jr.'
    adp_df.loc[adp_df['Name'] == 'Scotty Miller', 'Name'] = 'Scott Miller'

    # 1. Merge with adp info
    test = pts_df_reg[['Player','Year','FantPos','Pts_PPR']].merge(adp_df[['Name', 'Year', 'Team', 'Position', 'AverageDraftPositionPPR']],
                        left_on = ['Player','Year','FantPos'], 
                        right_on = ['Name', 'Year', 'Position'],
                        how = 'outer',
                        indicator= 'foundAdp')
    # print(test.groupby(['Year']))
    a = test[['Year','foundAdp']].value_counts().reset_index().sort_values(['Year','foundAdp'])
    print(a)
    # print(test.shape)
    
    # 2. Create previous year, fill out player name, position, team
    test['PrvYear'] = test['Year'] - 1
    test['Player'].fillna(test['Name'], inplace=True)
    test.drop('Name',axis = 1, inplace= True)
    test['FantPos'].fillna(test['Position'], inplace=True)
    test.drop('Position',axis = 1, inplace= True)
    # test['Tm'].fillna(test['Team'], inplace = True)
    test.drop('Team', axis = 1, inplace= True)

    # 3. Create positional dummies
    test[['QB','RB','TE','WR']] = pd.get_dummies(test['FantPos'])
    return test
    
def main():
    scoring_type = 'PPR' # or HPPR or NPPR
    scoring = 'Pts_' + scoring_type

    path = pathlib.Path(__file__).parent.resolve()
    os.chdir(path)

    adp_pickle = '../data/created/adp.p'
    points_pickle = '../data/created/points.p'
    
    with open(adp_pickle, 'rb') as handle:
        adp_df = pickle.load(handle)
    with open(points_pickle, 'rb') as handle:
        points_df_dict = pickle.load(handle)

    pc = PointsConverter(ScoringType.PPR)
    points_df = pc.prep_pts_df(points_df_dict)

    final_df = merge_adp_dataset(points_df, adp_df)
    df1 = final_df[final_df['foundAdp'] == 'left_only']
    df2 = df1[(df1['Pts_PPR'] >= 20) & (df1['Year'] > 2015)]
    print(df2)
    # print(df2.sort_values(['Pts_PPR'], ascending = False).head(40))
    # print(final_df[final_df['foundAdp'] == 'left_only'].tail(100))
    # print(final_df[final_df['foundAdp'] == 'right_only'].tail(100))

if __name__ == '__main__':
    main()