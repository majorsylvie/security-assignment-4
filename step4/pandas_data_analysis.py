import pandas as pd

TOPSITES = "step4-topsites-certs.csv"
OTHERSITES = "step4-othersites-certs.csv"

def analyze_csv(csv_path="topsite_small.csvOUTPUT.csv"):
    """
    function to take in a dataframe with column format:
        index,
        ranking,
        domain,
        org_name,
        time_difference_in_seconds_float,
        crypto_algorithm,
        pub_key_len,
        pub_key_exp,
        sign_alg

    and do all the data analsis I want for step 4
    """
    # since I forgot to remove the index when 
    # storing my final results in the CSV
    # I will ignore the first column as it tells me nothing
    # that the ranking does not already
    # https://stackoverflow.com/questions/46755669/how-to-read-csv-avoid-index?rq=3
    # if I don't do this another column of the index ets added
    # which looks very silly :p
    df = pd.read_csv(csv_path, index_col=[0])

    # similarly, the method I used to update the pandas dataframe
    # actually kept the headers from before
    # thus the very first row of the CSV
    # is 0, ranking, domain,,,,,,
    # which is not relevant to my data analysis
    # and I don't want "ranking" nor "domain" to show up 
    # in data analysis, so I will remove that row
    # drop code taken from pandas documentation
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.drop.html
    df.drop(index=0, inplace=True)

    print(df)
    return df

if __name__ == "__main__":
    analyze_csv(TOPSITES)
    analyze_csv(OTHERSITES)


