from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from snowflake.snowpark.session import Session
import json

# passphrase=b'abcxyz'

'''
https://stackoverflow.com/questions/35978211/convert-pem-file-to-der
'''
def get_session(json_path = "credentials_sf.json"):
    with open('rsa_key.p8', 'rb') as xl_file:

        private_key = xl_file.read()
    p_key= serialization.load_pem_private_key(
        private_key,
        password =None,
        # password=passphrase,
        backend=default_backend()
        )

    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())



    connection_parameters = {

    }
    with open(json_path) as f:
        connection_parameters = json.load(f)
    connection_parameters['private_key'] = pkb
    session = Session.builder.configs(connection_parameters).create()
    return session