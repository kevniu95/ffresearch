import pickle
import pathlib
import os


def loadData(adp, points):
    with open(adp, 'rb') as handle:
        adp_df = pickle.load(handle)

    with open(points, 'rb') as handle:
        points_df = pickle.load(handle)
    
    print(adp_df)
    print(points_df)

    

    
def main():
    path = pathlib.Path(__file__).parent.resolve()
    os.chdir(path)

    adp_pickle = '../data/created/adp.p'
    points_pickle = '../data/created/points.p'

if __name__ == '__main__':
    main()