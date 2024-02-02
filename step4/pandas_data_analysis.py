import pandas as pd

TOPSITES = "step4-topsites-certs.csv"
OTHERSITES = "step4-othersites-certs.csv"

def read_certs_csv(csv_path="topsite_small.csvOUTPUT.csv"):
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
    print(df.columns)
    return df

def analyze_df(df):
    """
    function to take in a dataframe generated by reading in the certificate information CSV and doing the following data analysis I want for step 4


    org_name sorted by the amount of ceritifcates issued
        subsorted alphabetically

    min and max  time_difference_in_seconds

    average and median time_differnce_in_seconds grouped by org_name

    BROADER COMPARISON across top and other

    dataframe/csv of cryptographic algorithm an frequency

        BROADER COMPARISON

    all unique key lengths

    all unique RSA public key exponents 
        BROADER COMPARISON ACROSS SITES

    dataframe/csv of signature algorithm to frequency
    """
    #ranking,domain,org_name,time_difference_in_seconds_float,crypto_algorithm,pub_key_len,pub_key_exp,sign_alg

    # org_name sorted by the amount of ceritifcates issued
    #     subsorted alphabetically
    df = df.sort_values(by='org_name')
    org_name_group = df.groupby('org_name')
    org_name_counts = org_name_group['org_name'].count().sort_values(ascending=False)
    print(f"org_name_counts = {org_name_counts}")

    print(f"==================================="); 

    #min and max  time_difference_in_seconds
    min_time_global = df['time_difference_in_seconds_float'].min()
    max_time_global = df['time_difference_in_seconds_float'].max()
    print(f"min valid cert time: {min_time_global * 60 * 60 * 24}")
    print(f"max valid cert time: {max_time_global * 60 * 60 * 24}")

    print()
    #average and median time_differnce_in_seconds grouped by org_name
    avg_time_by_cert = org_name_group['time_difference_in_seconds_float'].mean().apply(lambda x: x/(60*60*24))
    print(f"avg validity time by cert:\n\n{avg_time_by_cert}")


    print(f"==================================="); 

    # dataframe/csv of cryptographic algorithm an frequency
    print(df['crypto_algorithm'])
    crypto_group = df.groupby('crypto_algorithm')
    crypto_counts = crypto_group['crypto_algorithm'].groups.keys()
    print(f"crypto_counts = {crypto_counts}")

if __name__ == "__main__":
    df = read_certs_csv(TOPSITES)
    print()
    analyze_df(df)
    # read_certs_csv(OTHERSITES)


