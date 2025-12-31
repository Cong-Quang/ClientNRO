class Config:
    # --- Server ---
    HOST = "103.245.255.222"
    PORT = 12451

    # --- Version ---
    VERSION = "2.3.5"

    # --- Account ---
    # List of accounts to run
    # You can add more accounts here
    ACCOUNTS = [
        {"username": "poopooi01", "password": "02082003"},
        #{"username": "poopooi03", "password": "02082003"},
        # {"username": "poopooi04", "password": "02082003"},
        # {"username": "poopooi05", "password": "02082003"},
    ]


    # From prompt: "Fukada:103.245.255.222:12451:0,0,0"
    # Assuming first part is server name, then IP, then Port.
