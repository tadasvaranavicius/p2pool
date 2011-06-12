from entangled.kademlia import node, encoding, protocol
from twisted.internet import defer

import bitcoin_p2p

class CustomBencode(encoding.Bencode):
    def __init__(self, prefix=""):
        self.prefix = prefix
    
    def encode(self, data):
        return self.prefix + encoding.Bencode.encode(self, data)
    
    def decode(self, data):
        if not data.startswith(self.prefix):
            raise ValueError("invalid prefix")
        return encoding.Bencode.decode(self, data[len(self.prefix):])

class Node(node.Node):
    @property
    def peers(self):
        for bucket in self._routingTable._buckets:
            for contact in bucket._contacts:
                yield contact
    
    def __init__(self, blockCallback, **kwargs):
        node.Node.__init__(self, networkProtocol=protocol.KademliaProtocol(self, msgEncoder=CustomBencode("p2pool")), **kwargs)
        self.blockCallback = blockCallback
    
    # disable data storage
    
    @node.rpcmethod
    def store(self, key, value, originalPublisherID=None, age=0, **kwargs):
        return
    
    @node.rpcmethod
    def findValue(self, key, value, originalPublisherID=None, age=0, **kwargs):
        return
    
    def _republishData(self, *args):
        return defer.succeed(None)
    
    # meat
    
    @node.rpcmethod
    def block(self, block_data):
        self.blockCallback(bitcoin_p2p.block.unpack(block_data))
