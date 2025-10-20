import os
import json
import logging
import requests
from web3 import Web3
from typing import Tuple
from dotenv import load_dotenv

# -------------------------------
# Settings
# -------------------------------
load_dotenv()
#INFURA_KEY = os.getenv('INFURA_KEY')
#RPC_URL = os.getenv('ETH_RPC_URL', f'https://mainnet.infura.io/v3/{INFURA_KEY}')
# Use Alchemy as fallback (free tier available at alchemy.com)
# RPC_URL = os.getenv('ETH_RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY')  # Or keep Infura if fixed
RPC_URL ="https://eth.llamarpc.com"
RPC_URL = "https://eth.drpc.org"
 
## Contract addresses
POSITION_MANAGER = Web3.to_checksum_address('0xC36442b4a4522E871399CD717aBDD847Ab11FE88')
FACTORY = Web3.to_checksum_address('0x1F98431c8aD98523631AE4a59f267346ea31F984')

# Your UNISWAP V3 NFT token ID
TOKEN_ID = 1099376

# -------------------------------
# Logging and Web3 Setup
# -------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
w3 = Web3(Web3.HTTPProvider(RPC_URL))  # Add verify=False if needed: Web3.HTTPProvider(RPC_URL, request_kwargs={'verify': False})
if not w3.is_connected():
    raise RuntimeError(f"Failed to connect to Ethereum RPC at {RPC_URL}")
logger.info(f"Connected to Ethereum Mainnet via your dedicated RPC endpoint.")
logger.info(f"Querying Uniswap V3 for NFT ID: {TOKEN_ID}")

# -------------------------------
# ABIs (Official for Uniswap V3)
# -------------------------------
POSITION_MANAGER_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"positions","outputs":[{"internalType":"uint96","name":"nonce","type":"uint96"},{"internalType":"address","name":"operator","type":"address"},{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"feeGrowthInside0LastX128","type":"uint256"},{"internalType":"uint256","name":"feeGrowthInside1LastX128","type":"uint256"},{"internalType":"uint128","name":"tokensOwed0","type":"uint128"},{"internalType":"uint128","name":"tokensOwed1","type":"uint128"}],"stateMutability":"view","type":"function"}]')
FACTORY_ABI = json.loads('[{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"}],"name":"getPool","outputs":[{"internalType":"address","name":"pool","type":"address"}],"stateMutability":"view","type":"function"}]')
POOL_ABI = json.loads('[{"inputs":[],"name":"feeGrowthGlobal0X128","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"feeGrowthGlobal1X128","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"slot0","outputs":[{"internalType":"uint160","name":"sqrtPriceX96","type":"uint160"},{"internalType":"int24","name":"tick","type":"int24"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"int24","name":"tick","type":"int24"}],"name":"ticks","outputs":[{"internalType":"uint128","name":"liquidityGross","type":"uint128"},{"internalType":"int128","name":"liquidityNet","type":"int128"},{"internalType":"uint256","name":"feeGrowthOutside0X128","type":"uint256"},{"internalType":"uint256","name":"feeGrowthOutside1X128","type":"uint256"}],"stateMutability":"view","type":"function"}]')
ERC20_ABI = json.loads('[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]')

# -------------------------------
# Contracts
# -------------------------------
pos_contract = w3.eth.contract(address=POSITION_MANAGER, abi=POSITION_MANAGER_ABI)
factory_contract = w3.eth.contract(address=FACTORY, abi=FACTORY_ABI)

# -------------------------------
# Fee Calculation Function
# -------------------------------
def get_unclaimed_fees(token_id: int) -> Tuple[float, float, str, str, str, str]:
    try:
        position_info = pos_contract.functions.positions(token_id).call()
        token0_addr, token1_addr, fee, tickLower, tickUpper, liquidity, feeGrowthInside0LastX128, feeGrowthInside1LastX128, tokensOwed0, tokensOwed1 = position_info[2:]

        if liquidity == 0 and tokensOwed0 == 0 and tokensOwed1 == 0:
            logger.warning(f"Position {token_id} has zero liquidity and no pending tokens.")
            return 0.0, 0.0, "N/A", "N/A", "N/A", "N/A"

        token0 = w3.eth.contract(address=token0_addr, abi=ERC20_ABI)
        token1 = w3.eth.contract(address=token1_addr, abi=ERC20_ABI)
        token0_sym, token1_sym = token0.functions.symbol().call(), token1.functions.symbol().call()
        token0_dec, token1_dec = token0.functions.decimals().call(), token1.functions.decimals().call()

        pool_address = factory_contract.functions.getPool(token0_addr, token1_addr, fee).call()
        pool_contract = w3.eth.contract(address=pool_address, abi=POOL_ABI)
        
        slot0 = pool_contract.functions.slot0().call()
        current_tick = slot0[1]
        
        feeGrowthGlobal0 = pool_contract.functions.feeGrowthGlobal0X128().call()
        feeGrowthGlobal1 = pool_contract.functions.feeGrowthGlobal1X128().call()

        tick_lower_info = pool_contract.functions.ticks(tickLower).call()
        tick_upper_info = pool_contract.functions.ticks(tickUpper).call()
        
        feeGrowthOutside0_lower, feeGrowthOutside1_lower = tick_lower_info[2:4]
        feeGrowthOutside0_upper, feeGrowthOutside1_upper = tick_upper_info[2:4]
        
        feeGrowthBelow0 = feeGrowthGlobal0 - feeGrowthOutside0_lower if current_tick < tickLower else feeGrowthOutside0_lower
        feeGrowthBelow1 = feeGrowthGlobal1 - feeGrowthOutside1_lower if current_tick < tickLower else feeGrowthOutside1_lower
        
        feeGrowthAbove0 = feeGrowthOutside0_upper if current_tick < tickUpper else feeGrowthGlobal0 - feeGrowthOutside0_upper
        feeGrowthAbove1 = feeGrowthOutside1_upper if current_tick < tickUpper else feeGrowthGlobal1 - feeGrowthOutside1_upper
        
        fees_owed0_wei = ((feeGrowthGlobal0 - feeGrowthBelow0 - feeGrowthAbove0) - feeGrowthInside0LastX128) * liquidity
        fees_owed1_wei = ((feeGrowthGlobal1 - feeGrowthBelow1 - feeGrowthAbove1) - feeGrowthInside1LastX128) * liquidity

        Q128 = 2**128
        total_fees0 = (fees_owed0_wei // Q128 + tokensOwed0) / (10**token0_dec)
        total_fees1 = (fees_owed1_wei // Q128 + tokensOwed1) / (10**token1_dec)

        logger.info(f"Calculated fees for V3 token ID {token_id}: {total_fees0} {token0_sym}, {total_fees1} {token1_sym}")
        return total_fees0, total_fees1, token0_sym, token1_sym, token0_addr, token1_addr

    except Exception as e:
        logger.error(f"Error calculating fees for token ID {token_id}: {str(e)}")
        raise

def get_token_price(address):
    url = f"https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={address}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get(address.lower(), {}).get('usd', 0)
    except Exception as e:
        print(f"Error fetching price for {address}: {e}")
        return 0

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    if "YOUR_INFURA_PROJECT_ID_HERE" in RPC_URL:
        print("Please replace 'YOUR_INFURA_PROJECT_ID_HERE' with your actual Infura Project ID.")
        exit(1)
        
    try:
        result = get_unclaimed_fees(TOKEN_ID)
        if result:
            fees0, fees1, symbol0, symbol1, token0_addr, token1_addr = result
            token0_price = get_token_price(token0_addr)
            token1_price = get_token_price(token1_addr)
            fees0_usd = fees0 * token0_price
            fees1_usd = fees1 * token1_price
            total_usd = fees0_usd + fees1_usd

            print(f"\n--- Unclaimed Fees for Uniswap V3 NFT ID: {TOKEN_ID} ---")
            print(f"Token 0: {fees0:.18f} {symbol0} (USD: {fees0_usd:.2f})")
            print(f"Token 1: {fees1:.18f} {symbol1} (USD: {fees1_usd:.2f})")
            print(f"Total USD: {total_usd:.2f}")
    except Exception as e:
        print(f"\nExecution failed. Please check the TOKEN_ID and your RPC connection.")
        print(f"Details: {str(e)}")
