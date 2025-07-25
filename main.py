from supabase import create_client
from datetime import datetime
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Load Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def check_account_exists(email: str) -> bool:
    username = email.split('@')[0]
    gmail_variant = f"{username}@gmail.com"
    diddy_variant = f"{username}@balldfaiof.com"

    response = supabase.table("accounts").select("id").eq("email", gmail_variant).execute()
    response2 = supabase.table("accounts").select("id").eq("email", diddy_variant).execute()
    
    return len(response.data) > 0 or len(response2.data) > 0 

async def create_chain_with_accounts(accounts_file, group: str):
    with open(accounts_file, 'r') as f:
        accounts = [line.strip().split(':') for line in f.readlines() if line.strip()]
    
    if not accounts:
        logger.error(f"No accounts found in {accounts_file}")
        return None, 0
    
    last_email = accounts[-1][0]
    logger.info(f"Checking if account {last_email} or its variant already exists in database")
    if await check_account_exists(last_email):
        logger.error(f"Account {last_email} or its variant already exists in database. Skipping file {accounts_file}")
        return None, 0

    try:
        chain_response = supabase.table("chains").insert({
            "created_at": datetime.now().isoformat()
        }).execute()
        
        chain_id = chain_response.data[0]['id']
        logger.info(f"Created chain with ID: {chain_id}")

        account_records = []
        for i, account in enumerate(accounts, 1):
            email = account[0]
            account_records.append({
                "chain_id": chain_id,
                "email": email,
                "password": "doordash1234",
                "created_at": datetime.now().isoformat(),
                "updated_at": None,
                "state": "unused",
                "account_index": i,
                "disabled": False,
                "account_group": group
            })

        accounts_response = supabase.table("accounts").insert(account_records).execute()
        logger.info(f"Created {len(accounts_response.data)} accounts")

        return chain_id, len(accounts_response.data)

    except Exception as e:
        logger.error(f"Error creating chain and accounts: {str(e)}")
        raise e

async def delete_chain(chain_id: str):
    try:
        supabase.table("accounts").delete().eq("chain_id", chain_id).execute()
        supabase.table("chains").delete().eq("id", chain_id).execute()
        logger.info(f"Deleted chain with ID: {chain_id}")
        logger.info(f"Deleted accounts for chain with ID: {chain_id}")
    except Exception as e:
        logger.error(f"Error deleting chain: {str(e)}")
        raise e

if __name__ == "__main__":
    import asyncio
    import glob

    async def process_all_chain_files():
        print("Choose account group:\n1 = default\n2 = squirtle")
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            group = "default"
        elif choice == "2":
            group = "squirtle"
        else:
            print("Invalid choice. Exiting.")
            return
        
        chain_files = glob.glob("chain-*.txt")
        results = []
        for file in chain_files:
            chain_id, num_accounts = await create_chain_with_accounts(file, group)
            if chain_id:
                results.append((file, chain_id, num_accounts))
        
        for file, chain_id, num_accounts in results:
            logger.info(f"File {file}: Created chain {chain_id} with {num_accounts} accounts")

    asyncio.run(process_all_chain_files())
