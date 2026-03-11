#!/usr/bin/env python3
"""
Simple test script to verify Snowflake connection using Snowpark.
This script uses the utilities from snowpark_utils.py to establish a connection
with credentials from credentials_sf.json and the private key from rsa_key.p8.
"""

from snowpark_utils import get_session

def test_snowflake_connection():
    """
    Test the connection to Snowflake by creating a session and running a simple query.
    """
    try:
        print("Attempting to connect to Snowflake...")
        # Create session using the utility function
        session = get_session()

        print("Session created successfully.")

        # Test the connection with a simple query
        result = session.sql("SELECT CURRENT_VERSION() AS version, CURRENT_ACCOUNT() AS account").collect()

        if result:
            version = result[0]['VERSION']
            account = result[0]['ACCOUNT']
            print("Connection successful!")
            print(f"Snowflake Version: {version}")
            print(f"Account: {account}")
        else:
            print("Query executed but no results returned.")

        # Close the session
        session.close()
        print("Session closed.")

    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    success = test_snowflake_connection()
    if success:
        print("\n✅ Snowflake connection test passed!")
    else:
        print("\n❌ Snowflake connection test failed!")