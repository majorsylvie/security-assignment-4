from  datetime import datetime
import ssl
import socket
import OpenSSL
import pandas as pd

def prepare_dataframe(cert_info_list_list):

    column_names = [
            'organization name',
            'validity duration',
            'crypto algo',
            'key length',
            'RSA exponent',
            'signature algo',
            ]
    df = pd.DataFrame(cert_info_list_list,columns=column_names)
    return df

#   YYYYMMDDhhmmssZ
def turn_ASN1_time_to_datetime(asn_time: bytes):
    """
    function to convert ASN times as given by the certs 
    to a date time
    YYYYMMDDhhmmssZ
    """

    # string should be 16 bytes
    
    # print(len(asn_time))
    assert len(asn_time) == 15

    # use datetime's cool ass
    # format string conversion to 
    # handle all the parsing for us
    asn_date = datetime.strptime(asn_time.decode('ascii'),"%Y%m%d%H%M%SZ")

    return asn_date

def find_second_difference_for_asn_times(asn_time_1: bytes, asn_time_2: bytes) -> float:
    date_1 = turn_ASN1_time_to_datetime(asn_time_1)
    date_2 = turn_ASN1_time_to_datetime(asn_time_2)

    date_1_timestamp = date_1.timestamp()
    date_2_timestamp = date_2.timestamp()

    second_difference = date_1_timestamp - date_2_timestamp

    second_difference = abs(second_difference)

    return second_difference

def get_row_for_website(website='google.com'):

    try:
        ctx = ssl.create_default_context()
        connection = socket.create_connection((website, 443))
        s = ctx.wrap_socket(connection, server_hostname=website)
        cert = s.getpeercert(True)
        s.close()
        cert = ssl.DER_cert_to_PEM_cert(cert)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert) 
    except Exception as e:
        print(f"got error: {website} : {e}")
        return []


    """
    cert fields I care about:
        organization name

        start time
        end time

        signature algorithm

        public key
            type
            len

        if OpenSSL.crypto.TYPE_RSA:
            public key expojnent

    """
    """
    map dictionary of:
        oganization name to count certificates issued
        and produce alphbetical list
            certificate amount and frequency per CA

        difference in times
            min
            max
            also patterns
            want to associate time difference and CA

        cryprtographic algorithms (pubkey type)
            frequency

        key lengths
            frequencty

        public key RSA exponent
            associate with CA



        rows with:
            immediate CA, time diff, crypto algo, key length, optional exponent, signature algorithm
    """



    # https://www.pyopenssl.org/en/latest/api/crypto.html

    org_name = x509.get_issuer().organizationName

    # The timestamps are formatted as an ASN.1 TIME:
    #   YYYYMMDDhhmmssZ
    # Watch out, these can return None.
    start_time = x509.get_notBefore()
    end_time = x509.get_notAfter()
    time_difference_in_seconds_float = find_second_difference_for_asn_times(start_time, end_time)

    sign_alg = x509.get_signature_algorithm()

    pub_key = x509.get_pubkey()
    pub_key_type = pub_key.type()

    # final class and name attributes
    # should extract the name of the class 
    # as a string, which is nicer than 
    # the type()
    # thanks stack overflow
    # https://stackoverflow.com/questions/75440/how-do-i-get-the-string-with-name-of-a-class
    # crypto_algorithm = pub_key.to_cryptography_key().__class__.__name__
    crypto_algorithm = None
    if pub_key_type == OpenSSL.crypto.TYPE_RSA: # 6
        crypo_algorithm = "RSA"
    elif pub_key_type == OpenSSL.crypto.TYPE_DSA: # 116
        crypo_algorithm = "DSA"
    elif pub_key_type == OpenSSL.crypto.TYPE_EC: # 408
        crypo_algorithm = "Elliptic Curve"
    elif pub_key_type == OpenSSL.crypto.TYPE_DH: # 28
        crypo_algorithm = "Diffie–Hellman"
    else:
        print(f"SOMEHOW GOT OTHER KEY: {pub_key_type}")

    """
    if pub_key_type == 6: #: OpenSSL.crypto.TYPE_RSA: # 6
        crypto_algorithm == "RSA:"
    elif pub_key_type == 116: # OpenSSL.crypto.TYPE_DSA: # 116
        crypto_algorithm = "DSA"
    elif pub_key_type == 408: # OpenSSL.crypto.TYPE_EC: # 408
        crypto_algorithm = "Elliptic Curve"
    elif pub_key_type == 28: #  OpenSSL.crypto.TYPE_DH: # 28
        crypto_algorithm = "Diffie–Hellman"
    else:
        print(f"SOMEHOW GOT OTHER KEY: {pub_key_type}")
    """
    pub_key_len = pub_key.bits()

    #6 RSA
    #116 DSA
    #408 EllipticCurve

    pub_key_exp = None
    if pub_key_type == OpenSSL.crypto.TYPE_RSA:
        pub_key_exp = pub_key.to_cryptography_key().public_numbers().e



    # structure for a single row in the eventually resultant dataframe
    # I will then later make a dataframe to get statistics from
    row = [
        org_name,
        time_difference_in_seconds_float,
        crypto_algorithm,
        pub_key_len,
        pub_key_exp,
        sign_alg
        ]

    print(row)
    return row
    
    """
    print(
            f"org_name = {org_name} : {type(org_name)}\n"
            f"start_time = {start_time} : {type(start_time)}\n"
            f"end_time = {end_time} : {type(end_time)}\n"
            f"crypto_alg ] {crypto_algorithm} : {type(crypto_algorithm)}\n"
            f"signature_alg ] {sign_alg} : {type(sign_alg)}\n"
            f"pub_key_type = {pub_key_type} : {type(pub_key_type)}\n"
            f"pub_key_len = {pub_key_len} : {type(pub_key_len)}\n"
            f"pub_key_exp = {pub_key_exp} : {type(pub_key_exp)}\n"
    )
    """



def try_domain_from_pandas_row(row):
    domain = row['domain']
    row = get_row_for_website(domain)
    return row

def try_csv(csv_path="topsite_small.csv"):
    df = pd.read_csv(csv_path, names=['ranking','domain'])
    ROW = 1
    application = df.apply(try_domain_from_pandas_row, axis=ROW)
    print(application)
    return

    # https://stackoverflow.com/questions/29550414/how-can-i-split-a-column-of-tuples-in-a-pandas-dataframe
    df[['HTTP availability','status code']] = pd.DataFrame(application.tolist(), index=df.index)

    # actually save the output to avoid misery of a useless long run

    # default path for testing input
    output_path = csv_path + "OUTPUT.csv"

    # requested output CSV names from assignment
    if csv_path == TOPSITES:
        output_path = "step3-topsites-requests.csv"
    elif csv_path == OTHERSITES:
        output_path = "step3-othersites-requests.csv"

    if output_path == csv_path:
        output_path += "_1.csv"

    print(df)
    df.to_csv(output_path)


def test_time_difference():
    asn1 = b"20240131103045Z"
    asn1 = b"20240201080808Z"
    asn2 = b"20250201080809Z"

    asn1 = b"20240201080808Z"
    diff = find_second_difference_for_asn_times(asn1,asn2)

    print(diff)

if __name__ == "__main__":
    try_csv()


