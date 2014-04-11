import os
import platform

from twisted.internet import defer

from . import data
from p2pool.util import math, pack, jsonrpc

@defer.inlineCallbacks
def check_genesis_block(bitcoind, genesis_block_hash):
    try:
        yield bitcoind.rpc_getblock(genesis_block_hash)
    except jsonrpc.Error_for_code(-5):
        defer.returnValue(False)
    else:
        defer.returnValue(True)

nets = dict(
   dilmacoin=math.Object(
        P2P_PREFIX='fbc0b6db'.decode('hex'),
        P2P_PORT=11056,
        ADDRESS_VERSION=48,
        RPC_PORT=21056,
        RPC_CHECK=defer.inlineCallbacks(lambda bitcoind: defer.returnValue(
            'litecoinaddress' in (yield bitcoind.rpc_help()) and
            not (yield bitcoind.rpc_getinfo())['testnet']
        )),
        SUBSIDY_FUNC=lambda height: 120*100000000 >> (height + 1)//210000,
        POW_FUNC=lambda data: pack.IntType(256).unpack(__import__('ltc_scrypt').getPoWHash(data)),
        BLOCK_PERIOD=480, # s
        SYMBOL='DILMA',
        CONF_FILE_FUNC=lambda: os.path.join(os.path.join(os.environ['APPDATA'], 'dilmacoin') if platform.system() == 'Windows' else os.path.expanduser('~/Library/Application Support/dilmacoin/') if platform.system() == 'Darwin' else os.path.expanduser('~/.dilmacoin'), 'coin.conf'),
        BLOCK_EXPLORER_URL_PREFIX='http://blockexplorer.dilmacoin.org/block/',
        ADDRESS_EXPLORER_URL_PREFIX='http://blockexplorer.dilmacoin.org/address/',
        TX_EXPLORER_URL_PREFIX='http://blockexplorer.dilmacoin.org/tx/',
        SANE_TARGET_RANGE=(2**256//1000000000 - 1, 2**256//1000 - 1),
        DUMB_SCRYPT_DIFF=2**16,
        DUST_THRESHOLD=0.03e8,
    ),
)
for net_name, net in nets.iteritems():
    net.NAME = net_name
