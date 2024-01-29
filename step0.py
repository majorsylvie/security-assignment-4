import pandas as pd

def create_tranco_df():
    # csv doesn't have column names
    # add them myself
    names=['ranking','domain']
    df = pd.read_csv("./tranco-1m-2024-01-25.csv",names=names)
    return df

def create_top_sites_df(tranco_dataframe):
    # this filters for sites with a ranking
    # smaller than 1000
    top_sites = tranco_dataframe[ tranco_dataframe['ranking'] <= 1000] 

    # there should always be 1000 top sites
    assert len(top_sites) == 1000

    return top_sites


def create_other_sites_df(tranco_dataframe):
    other_sites = tranco_dataframe[ tranco_dataframe['ranking'] % 1000 == 0] 

    # the above code includes the 1000th ranked site
    # this ensures it's not included
    other_sites = other_sites[other_sites['ranking'] > 1000]

    # since there are 1 million ranked sites
    # and were including 1/1000th of them
    # and dropping the 1st 1000th, then 
    # we should have 999 sites
    assert len(other_sites) == 999
    return other_sites

def make_csv_for_all_dataframes():
    tranco = create_tranco_df()

    assert isinstance(tranco,pd.DataFrame)

    top = create_top_sites_df(tranco)
    other = create_other_sites_df(tranco)

    assert isinstance(top,pd.DataFrame)
    assert isinstance(other,pd.DataFrame)

    top.to_csv("step0-topsites.csv")
    other.to_csv("step0-othersites.csv")

    


if __name__ == "__main__":
    make_csv_for_all_dataframes()
