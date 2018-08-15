#!/usr/bin/env python3
# (C)opyright 2018 /u/awemany
# Code to generate a 'stream of transactions'. That is, a list of transactions
# with interdependencies in a partial (causal) order that could be observed by an omniscient
# entity, would it observe transaction *signing* time from a point in space time.
# You can look at this generating a "blockchain" like it is now, but without the blocks.
# So just the transactions in the natural order that they appear in.
#
from numpy.random import randint
from numpy import random
import pickle
from parameters import *

# keeps track of any TXID floating around anywhere in the system
# This is to ensure the equivalent of the much talked about 'DAG property'
issued_txids = set()
def newTXID():
    """ Generate a new unique TXID. Keep track of TXIDs issued. """
    while True:
        # make sure the TXIDs are unique ... birthdays come fast
        x = randint(0, 1<<20)
        if x not in issued_txids:
            issued_txids.add(x)
            return x

def inputDistribution():
    """Probability distribution of number of outputs for a transaction.
    We ignore the special case of coinbases for now and therefore all
    transactions should have at least one input.
    """
    return randint(1, 4)

def outputDistribution():
    """Probability distribution of number of outputs for a transaction.
    We ignore 'free for miner' transaction special cases, and
    therefore all transactions should have at least one output.
    The expected value <#output * outp_distribution - #inp * inp-distribution>
    should correspond to UTXO set size growth.
    """
    return randint(1, 5)

def inputDistanceDistributions(N):
    """ Given the number of inputs, this returns the distance into the
    past (in number of transactions, as a positive value) of each of the inputs.

    The transaction generator will try this distribution. When it fails, it will
    introduce a weird bias (as a trade-off for accuracy) by choosing a random direction to go
    into until it hits a consumable input.
    """
    res=[]
    for i in range(N):
        res.append(int(random.exponential(scale = 1000.)))
    return res

def makeTransaction(stream, utxo, num_utxo):
    """Given the current stream of transactions 'stream' and the unspent
    outputs available in utxo (which is a map of TXID ->
    number-of-outputs-left), this creates a new transaction and
    inserts it into stream as well as the available outputs map (instantaneous utxo view)
    num_utxo is the number of unspent outputs available before the
    transaction is inserted. The new number of unspent outputs will be
    returned.
    """
    n_inp = min(inputDistribution(), num_utxo)
    n_out = outputDistribution()

    txid = newTXID()
    inputs = []

    dists = inputDistanceDistributions(n_inp)
    for d in dists:
        d = d % len(stream)
        ref_txid, ref_inputs, ref_outputs = stream[-d]
        if ref_txid not in utxo:
            # not available - go into random direction to find consumable input (and wrap around). will always find consumable input due to num_utxo constraint. crude and biased but hopefully not too badly.
            search_dir = random.randint(0,1)
            while not ref_txid in utxo:
                d=(d+1 if search_dir else d-1) % len(stream)
                ref_txid, ref_inputs, ref_outputs = stream[-d]

        assert ref_txid in utxo
        assert(utxo[ref_txid] > 0)
        utxo[ref_txid]-=1
        if utxo[ref_txid] == 0:
            del utxo[ref_txid]

        inputs.append(ref_txid)

    stream.append((txid, inputs, n_out))
    utxo[txid]=n_out

    return num_utxo + n_out - n_inp

stream = [] # stream of transactions
utxo={}
num_utxo = 0

for i in range(N_CHAIN + N_BLOCK):
    num_utxo = makeTransaction(stream, utxo, num_utxo)
    if i == N_CHAIN-1:
        # At the block boundary, save the UTXO set for potential later reuse
        utxo0 = utxo.copy()
    if (i% 10000) == 0:
        print("@", i)

with open("stream.dat", "wb") as outf:
        pickle.dump((stream, utxo0, utxo), outf)
