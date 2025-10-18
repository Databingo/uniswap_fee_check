import requests
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
INFURA_KEY = os.getenv('INFURA_KEY')
RPC_URL = os.getenv('ETH_RPC_URL', f'https://mainnet.infura.io/v3/{INFURA_KEY}')
# Use Alchemy as fallback (free tier available at alchemy.com)
# RPC_URL = os.getenv('ETH_RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY')

## Contract addresses
POSITION_MANAGER = Web3.to_checksum_address('0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e')
STATE_VIEW = Web3.to_checksum_address('0x7ffe42c4a5deea5b0fec41c94c136cf115597227')

# Position token ID
TOKEN_ID = 85000  # Test with 85000 

w3 = Web3(Web3.HTTPProvider(RPC_URL))  # Add verify=False if needed: Web3.HTTPProvider(RPC_URL, request_kwargs={'verify': False}))

# ABI for PositionManager.getPoolAndPositionInfo
position_manager_abi = [
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "getPoolAndPositionInfo",
        "outputs": [
            {
                "components": [
                    {"internalType": "Currency", "name": "currency0", "type": "address"},
                    {"internalType": "Currency", "name": "currency1", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "int24", "name": "tickSpacing", "type": "int24"},
                    {"internalType": "address", "name": "hooks", "type": "address"}
                ],
                "internalType": "struct PoolKey",
                "name": "poolKey",
                "type": "tuple"
            },
            {"internalType": "uint256", "name": "info", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# ERC-721 ABI for ownerOf
erc721_abi = [
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "ownerOf",
        "outputs": [{"internalType": "address", "name": "owner", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# ABI for StateView.getPositionInfo and getFeeGrowthInside
state_view_abi = [
    {
        "inputs": [
            {"internalType": "PoolId", "name": "", "type": "bytes32"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "int24", "name": "", "type": "int24"},
            {"internalType": "int24", "name": "", "type": "int24"},
            {"internalType": "bytes32", "name": "", "type": "bytes32"}
        ],
        "name": "getPositionInfo",
        "outputs": [
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "feeGrowthInside0LastX128", "type": "uint256"},
            {"internalType": "uint256", "name": "feeGrowthInside1LastX128", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "PoolId", "name": "", "type": "bytes32"},
            {"internalType": "int24", "name": "", "type": "int24"},
            {"internalType": "int24", "name": "", "type": "int24"}
        ],
        "name": "getFeeGrowthInside",
        "outputs": [
            {"internalType": "uint256", "name": "feeGrowthInside0X128", "type": "uint256"},
            {"internalType": "uint256", "name": "feeGrowthInside1X128", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# ERC20 ABI for decimals
erc20_abi = [
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

position_manager = w3.eth.contract(address=POSITION_MANAGER, abi=position_manager_abi)
state_view = w3.eth.contract(address=STATE_VIEW, abi=state_view_abi)
erc721 = w3.eth.contract(address=POSITION_MANAGER, abi=erc721_abi)

def get_token_price(address):
    zero_address = '0x0000000000000000000000000000000000000000'
    if address == zero_address:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        try:
            response = requests.get(url)
            data = response.json()
            return data.get('ethereum', {}).get('usd', 0)
        except Exception as e:
            print(f"Error fetching ETH price: {e}")
            return 0
    else:
        url = f"https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={address}&vs_currencies=usd"
        try:
            response = requests.get(url)
            data = response.json()
            return data.get(address.lower(), {}).get('usd', 0)
        except Exception as e:
            print(f"Error fetching price for {address}: {e}")
            return 0

try:
    # Step 1: Check if position is minted
    try:
        owner = erc721.functions.ownerOf(TOKEN_ID).call()
        if owner == '0x0000000000000000000000000000000000000000':
            print(f"Position {TOKEN_ID} is burned (no owner). Fees: 0")
            print("Accrued Fees:")
            print("Token0: 0 (USD: 0.00)")
            print("Token1: 0 (USD: 0.00)")
            print("Total USD: 0.00")
            exit(0)
    except Exception as owner_error:
        print(f"Position {TOKEN_ID} not minted (revert on ownerOf). Fees: 0")
        print("Accrued Fees:")
        print("Token0: 0 (USD: 0.00)")
        print("Token1: 0 (USD: 0.00)")
        print("Total USD: 0.00")
        exit(0)

    # Step 2: Get poolKey and packed info
    try:
        pool_key, info = position_manager.functions.getPoolAndPositionInfo(TOKEN_ID).call()
    except Exception as e:
        print(f"Error fetching poolKey/info: {e}. Position data unavailable. Fees: 0")
        print("Accrued Fees:")
        print("Token0: 0 (USD: 0.00)")
        print("Token1: 0 (USD: 0.00)")
        print("Total USD: 0.00")
        exit(0)

    # Decode ticks from info (packed uint256)
    tick_upper = (info >> 32) & 0xFFFFFF
    if tick_upper >= 0x800000:
        tick_upper -= 0x1000000
    tick_lower = (info >> 8) & 0xFFFFFF
    if tick_lower >= 0x800000:
        tick_lower -= 0x1000000

    # PoolId is keccak256(abi.encode(poolKey))
    pool_id = w3.keccak(w3.codec.encode(['(address,address,uint24,int24,address)'], [(pool_key[0], pool_key[1], pool_key[2], pool_key[3], pool_key[4])]))

    # Salt is bytes32(tokenId)
    salt = TOKEN_ID.to_bytes(32, 'big')

    # Owner is PositionManager
    owner = POSITION_MANAGER

    # Step 3: Get position info
    try:
        liquidity, fee_growth_inside0_last, fee_growth_inside1_last = state_view.functions.getPositionInfo(pool_id, owner, tick_lower, tick_upper, salt).call()
    except Exception as e:
        print(f"Error fetching position info: {e}. Possibly inactive. Fees: 0")
        print("Accrued Fees:")
        print("Token0: 0 (USD: 0.00)")
        print("Token1: 0 (USD: 0.00)")
        print("Total USD: 0.00")
        exit(0)

    # Step 4: Get current fee growth inside
    try:
        fee_growth_inside0_current, fee_growth_inside1_current = state_view.functions.getFeeGrowthInside(pool_id, tick_lower, tick_upper).call()
    except Exception as e:
        print(f"Error fetching fee growth: {e}. Fees: 0")
        print("Accrued Fees:")
        print("Token0: 0 (USD: 0.00)")
        print("Token1: 0 (USD: 0.00)")
        print("Total USD: 0.00")
        exit(0)

    # Calculate unclaimed fees
    Q128 = 1 << 128
    token0_fees = ((fee_growth_inside0_current - fee_growth_inside0_last) * liquidity) // Q128 if fee_growth_inside0_current >= fee_growth_inside0_last else 0
    token1_fees = ((fee_growth_inside1_current - fee_growth_inside1_last) * liquidity) // Q128 if fee_growth_inside1_current >= fee_growth_inside1_last else 0

    # Step 5: Get decimals for tokens, handle zero address (ETH)
    zero_address = '0x0000000000000000000000000000000000000000'
    token0_decimals = 18  # Default for ETH or invalid
    token1_decimals = 18  # Default for ETH or invalid
    token0_name = "ETH" if pool_key[0] == zero_address else pool_key[0]
    token1_name = "ETH" if pool_key[1] == zero_address else pool_key[1]

    if pool_key[0] != zero_address:
        try:
            token0_contract = w3.eth.contract(address=pool_key[0], abi=erc20_abi)
            token0_decimals = token0_contract.functions.decimals().call()
        except Exception as e:
            print(f"Error fetching decimals for Token0 ({pool_key[0]}): {e}. Assuming 18 decimals.")
    else:
        print(f"Token0 is ETH (zero address). Using 18 decimals.")

    if pool_key[1] != zero_address:
        try:
            token1_contract = w3.eth.contract(address=pool_key[1], abi=erc20_abi)
            token1_decimals = token1_contract.functions.decimals().call()
        except Exception as e:
            print(f"Error fetching decimals for Token1 ({pool_key[1]}): {e}. Assuming 18 decimals.")
    else:
        print(f"Token1 is ETH (zero address). Using 18 decimals.")

    # Adjust fees for decimals
    token0_fees_adjusted = token0_fees / (10 ** token0_decimals)
    token1_fees_adjusted = token1_fees / (10 ** token1_decimals)

    # Get USD prices, handle ETH for zero address
    token0_price = get_token_price(pool_key[0])
    token1_price = get_token_price(pool_key[1])

    # Calculate USD values
    token0_usd = token0_fees_adjusted * token0_price
    token1_usd = token1_fees_adjusted * token1_price
    total_usd = token0_usd + token1_usd

    print(f"Accrued Fees:")
    print(f"Token0 ({token0_name}): {token0_fees_adjusted} (USD: {token0_usd:.2f})")
    print(f"Token1 ({token1_name}): {token1_fees_adjusted} (USD: {token1_usd:.2f})")
    print(f"Total USD: {total_usd:.2f}")
except Exception as e:
    print(f"Unexpected error: {e}")
    print("Try unsetting proxies, updating libraries, or using verify=False (insecure).")
