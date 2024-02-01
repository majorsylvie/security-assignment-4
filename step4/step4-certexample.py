from  datetime import datetime
import ssl
import socket
import OpenSSL

website = 'google.com'
ctx = ssl.create_default_context()
connection = socket.create_connection((website, 443))
s = ctx.wrap_socket(connection, server_hostname=website)
cert = s.getpeercert(True)
s.close()
cert = ssl.DER_cert_to_PEM_cert(cert)
x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert) 
print(x509)

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
    oganization name to count

    difference in times

"""

# https://www.pyopenssl.org/en/latest/api/crypto.html

org_name = x509.get_issuer().organizationName

# The timestamps are formatted as an ASN.1 TIME:
#   YYYYMMDDhhmmssZ
# Watch out, these can return None.
start_time = x509.get_notBefore()
end_time = x509.get_notAfter()

sign_alg = x509.get_signature_algorithm()

pub_key = x509.get_pubkey()
pub_key_type = pub_key.type()
pub_key_len = pub_key.bits()

#6 RSA
#116 DSA
#408 EllipticCurve

pub_key_exp = None
if pub_key_type == OpenSSL.crypto.TYPE_RSA:
    pub_key_exp = pub_key.to_cryptography_key().public_numbers().exponent()

print(
        f"org_name = {org_name} : {type(org_name)}\n"
        f"start_time = {start_time} : {type(start_time)}\n"
        f"end_time = {end_time} : {type(end_time)}\n"
        f"signature_alg ] {sign_alg} : {type(sign_alg)}\n"
        f"pub_key_type = {pub_key_type} : {type(pub_key_type)}\n"
        f"pub_key_len = {pub_key_len} : {type(pub_key_len)}\n"
        f"pub_key_exp = {pub_key_exp} : {type(pub_key_exp)}\n"
)




#   YYYYMMDDhhmmssZ
def turn_ASN1_time_to_datetime(asn_time: bytes):
    """
    function to convert ASN times as given by the certs 
    to a date time
    YYYYMMDDhhmmssZ
    """

    # string should be 16 bytes
    
    print(len(asn_time))
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



if __name__ == "__main__":
    asn1 = b"20240131103045Z"
    asn1 = b"20240201080808Z"
    asn2 = b"20250201080809Z"

    asn1 = b"20240201080808Z"
    diff = find_second_difference_for_asn_times(asn1,asn2)

    print(diff)


