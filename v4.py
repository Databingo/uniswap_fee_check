import requests
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()
# INFURA_KEY = os.getenv('INFURA_KEY')
# RPC_URL = os.getenv('ETH_RPC_URL', f'https://mainnet.infura.io/v3/{INFURA_KEY}')
# Use Alchemy as fallback (free tier available at alchemy.com)
# RPC_URL = os.getenv('ETH_RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY')
RPC_URL = "https://eth.llamarpc.com"
RPC_URL = "https://eth.drpc.org"
RPC_URL = "https://eth-mainnet.public.blastapi.io"
RPC_URL = "https://rpc.payload.de"

# Position token ID
TOKEN_ID = 85000  # Test with 85000 
 
w3 = Web3(Web3.HTTPProvider(RPC_URL))  # Add verify=False if needed: Web3.HTTPProvider(RPC_URL, request_kwargs={'verify': False}))

# --- Core addresses ---
POSITION_MANAGER = Web3.to_checksum_address('0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e')
STATE_VIEW = Web3.to_checksum_address('0x7ffe42c4a5deea5b0fec41c94c136cf115597227')
WETH_ADDRESS = Web3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
CHAINLINK_ETH_USD = Web3.to_checksum_address("0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419")
V4_POOL_MANAGER =  Web3.to_checksum_address('0x000000000004444c5dc75cB358380D2e3dE08A90')
V4_STATE_VIEW = Web3.to_checksum_address('0x7ffe42c4a5deea5b0fec41c94c136cf115597227')

ZERO = '0x0000000000000000000000000000000000000000'

# --- ABIs ---
position_manager_abi = [{
    "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
    "name": "getPoolAndPositionInfo",
    "outputs": [{
        "components": [
            {"internalType": "address", "name": "currency0", "type": "address"},
            {"internalType": "address", "name": "currency1", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"},
            {"internalType": "int24", "name": "tickSpacing", "type": "int24"},
            {"internalType": "address", "name": "hooks", "type": "address"}],
        "internalType": "struct PoolKey", "name": "poolKey", "type": "tuple"},
        {"internalType": "uint256", "name": "info", "type": "uint256"}],
    "stateMutability": "view", "type": "function"}]

v4_pool_manager_abi = [{
        "inputs": [
            {"internalType": "address", "name": "currency0", "type": "address"},
            {"internalType": "address", "name": "currency1", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"},
            {"internalType": "int24", "name": "tickSpacing", "type": "int24"},
            {"internalType": "address", "name": "hooks", "type": "address"}
        ],
        "name": "getPool",
        "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }]

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

v4_state_view_abi =  [{
    "inputs": [{"internalType": "bytes32", "name": "poolId", "type": "bytes32"}],
    "name": "getSlot0",
    "outputs": [
        {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
        {"internalType": "int24", "name": "tick", "type": "int24"}
    ],
    "stateMutability": "view", "type": "function"
}]

erc721_abi = [{
    "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
    "name": "ownerOf",
    "outputs": [{"internalType": "address", "name": "owner", "type": "address"}],
    "stateMutability": "view", "type": "function"}]

erc20_abi = [{"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
              "stateMutability": "view", "type": "function"}]

v3_factory_abi = [{"inputs": [{"internalType": "address", "name": "tokenA", "type": "address"},
                              {"internalType": "address", "name": "tokenB", "type": "address"},
                              {"internalType": "uint24", "name": "fee", "type": "uint24"}],
                   "name": "getPool", "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
                   "stateMutability": "view", "type": "function"}]

v2_factory_abi = [{"inputs": [{"internalType": "address", "name": "tokenA", "type": "address"},
                              {"internalType": "address", "name": "tokenB", "type": "address"}],
                   "name": "getPair", "outputs": [{"internalType": "address", "name": "pair", "type": "address"}],
                   "stateMutability": "view", "type": "function"}]

chainlink_abi = [{"inputs": [], "name": "latestAnswer", "outputs": [{"internalType": "int256", "name": "", "type": "int256"}],
                  "stateMutability": "view", "type": "function"}]

# --- Contracts ---
position_manager = w3.eth.contract(address=POSITION_MANAGER, abi=position_manager_abi)
state_view = w3.eth.contract(address=STATE_VIEW, abi=state_view_abi)
erc721 = w3.eth.contract(address=POSITION_MANAGER, abi=erc721_abi)
v3_factory = w3.eth.contract(address=Web3.to_checksum_address("0x1F98431c8aD98523631AE4a59f267346ea31F984"), abi=v3_factory_abi)
v2_factory = w3.eth.contract(address=Web3.to_checksum_address("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"), abi=v2_factory_abi)
chainlink_eth = w3.eth.contract(address=CHAINLINK_ETH_USD, abi=chainlink_abi)
#v4_pool_manager = w3.eth.contract(address=V4_POOL_MANAGER, abi=v4_pool_manager_abi)
#v4_state_view = w3.eth.contract(address=V4_STATE_VIEW, abi=v4_state_view_abi)


def get_v4_price(token_address):
    """Try to get price from Uniswap V4 via PoolManager + StateView."""
    try:
        token_address = Web3.to_checksum_address(token_address)
        if token_address in [ZERO, WETH_ADDRESS]:
            return get_eth_price()

        token_decimals = get_decimals(token_address)
        weth_decimals = get_decimals(WETH_ADDRESS)
        eth_usd = get_eth_price()

        # V4 canonical ordering: currency0 < currency1
        a, b = (token_address, WETH_ADDRESS)
        if a.lower() > b.lower():
            a, b = b, a

        # typical v4 fees & tick spacings
        fee_tiers = [500, 3000, 10000]
        tick_spacings = [1, 10, 60, 200]

        for fee in fee_tiers:
            for tick_spacing in tick_spacings:
                pool_key = (a, b, fee, tick_spacing, ZERO)
                pool_id = w3.keccak(
                    w3.codec.encode(
                        ['(address,address,uint24,int24,address)'],
                        [pool_key]
                    )
                )
                try:
                    slot0 = v4_state_view.functions.getSlot0(pool_id).call()
                    sqrtPriceX96 = slot0[0]
                    if sqrtPriceX96 == 0:
                        continue

                    ## Determine which token was token0
                    token0, token1 = a, b
                    # Normalize for decimals
                    if token0.lower() == token_address.lower():
                        price_token_in_weth = (sqrtPriceX96 ** 2 / 2 ** 192) * (10 ** (token_decimals - weth_decimals))
                    else:
                        price_token_in_weth = (2 ** 192 / sqrtPriceX96 ** 2) * (10 ** (token_decimals - weth_decimals))
                    print(f"[V4] Found pool for {token_address} fee {fee} tickSpacing {tick_spacing}")
                    return price_token_in_weth * eth_usd

                except Exception:
                    continue

    except Exception as e:
        print(f"[V4] Error: {e}")
    return 0

# --- Helpers ---
def get_eth_price():
    return chainlink_eth.functions.latestAnswer().call() / 1e8  # Chainlink ETH/USD

def get_decimals(token):
    if token in [ZERO, WETH_ADDRESS]:
        return 18
    try:
        contract = w3.eth.contract(address=token, abi=erc20_abi)
        return contract.functions.decimals().call()
    except:
        return 18

def get_token_price(token_address):
    token_address = Web3.to_checksum_address(token_address)
    if token_address in [ZERO, WETH_ADDRESS]:
        return get_eth_price()

    token_decimals = get_decimals(token_address)
    weth_decimals = get_decimals(WETH_ADDRESS)
    eth_usd = get_eth_price()

    # --- Try Uniswap V4 first --- not work yet
    #v4_price = get_v4_price(token_address)
    #if v4_price > 0:
    #    return v4_price
    #print(f"{token_address} V4 failed, trying V3...")

    # --- Try Uniswap V3 ---
    fee_tiers = [500, 3000, 10000]
    for fee in fee_tiers:
        try:
            pool = v3_factory.functions.getPool(token_address, WETH_ADDRESS, fee).call()
            if pool != ZERO:
                pool_abi = [
                    {"inputs": [], "name": "slot0",
                     "outputs": [{"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
                                 {"internalType": "int24", "name": "tick", "type": "int24"},
                                 {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
                                 {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
                                 {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
                                 {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
                                 {"internalType": "bool", "name": "unlocked", "type": "bool"}],
                     "stateMutability": "view", "type": "function"},
                    {"inputs": [], "name": "token0",
                     "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                     "stateMutability": "view", "type": "function"},
                    {"inputs": [], "name": "token1",
                     "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                     "stateMutability": "view", "type": "function"},
                ]
                pool_c = w3.eth.contract(address=pool, abi=pool_abi)
                sqrtPriceX96 = pool_c.functions.slot0().call()[0]
                t0 = pool_c.functions.token0().call()
                t1 = pool_c.functions.token1().call()

                if sqrtPriceX96 == 0:
                    continue

                # Normalize for decimals
                if t0.lower() == token_address.lower():
                    price_token_in_weth = (sqrtPriceX96 ** 2 / 2 ** 192) * (10 ** (token_decimals - weth_decimals))
                else:
                    price_token_in_weth = (2 ** 192 / sqrtPriceX96 ** 2) * (10 ** (token_decimals - weth_decimals))

                return price_token_in_weth * eth_usd
        except Exception:
            continue
    print("V3 failed try V2")

    # --- Try Uniswap V2 ---
    try:
        pair = v2_factory.functions.getPair(token_address, WETH_ADDRESS).call()
        if pair != ZERO:
            pair_abi = [
                {"inputs": [], "name": "getReserves",
                 "outputs": [{"internalType": "uint112", "name": "reserve0", "type": "uint112"},
                             {"internalType": "uint112", "name": "reserve1", "type": "uint112"},
                             {"internalType": "uint32", "name": "blockTimestampLast", "type": "uint32"}],
                 "stateMutability": "view", "type": "function"},
                {"inputs": [], "name": "token0",
                 "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                 "stateMutability": "view", "type": "function"},
                {"inputs": [], "name": "token1",
                 "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                 "stateMutability": "view", "type": "function"}
            ]
            pair_c = w3.eth.contract(address=pair, abi=pair_abi)
            reserves = pair_c.functions.getReserves().call()
            r0, r1 = reserves[0], reserves[1]
            t0 = pair_c.functions.token0().call()
            t1 = pair_c.functions.token1().call()
            if r0 == 0 or r1 == 0:
                return 0
            if t0.lower() == token_address.lower():
                price_token_in_weth = r1 / r0 * (10 ** (token_decimals - weth_decimals))
            else:
                price_token_in_weth = r0 / r1 * (10 ** (token_decimals - weth_decimals))
            return price_token_in_weth * eth_usd
    except Exception:
        pass

    return 0

# Get Fee and Price
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
