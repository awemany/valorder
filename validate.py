#!/usr/bin/env python3
import collections
import pickle
import pprint
from parameters import *

# OTI: _Output _then _Input validation (name for tomtomtom7's scheme, unless there's a
# better one available?)

# utxo0: UTXO set after N_CHAIN transactions and just before start of block
stream, utxo0, utxo_final = pickle.load(open("stream.dat", "rb"))

block = stream[-N_BLOCK:]

# keep access stats
stats=collections.Counter()

n_workers = 5

assert N_BLOCK % n_workers == 0

# OTI_Worker:
# validation 'worker' that validates outputs first then inputs, like it is
# proposed for doing validation exploiting the DAG property and update the stats for
# global vs. local UTXO accesses.

def OTI_Worker_processOutputs(global_utxo, chunk):
    local_utxo = {}

    for txid, inputs, outputs in chunk:
        # Note: no explicit output loop here as outputs are simply abstracted as an integer
        # save into local set
        stats["local_writes"]+=1
        local_utxo[txid] = outputs

    return local_utxo

def OTI_Worker_processInputs(global_utxo, local_utxo, chunk):
    for txid, inputs, outputs in chunk:
        for inp in inputs:
            stats["local_reads"]+=1
            stats["local_writes"]+=1
            if inp in local_utxo:
                local_utxo[inp]-=1
                if local_utxo[inp] == 0:
                    del local_utxo[inp]
            else:
                local_utxo[inp]=-1

def OTI_Worker_Commit(global_utxo, local_utxo):
    for txid, delta in local_utxo.items():
        stats["local_reads"]+=1
        stats["global_writes"]+=1
        if txid in global_utxo:
            global_utxo[txid]+=delta
        else:
            global_utxo[txid]=delta


def ValidateOutsThenIns(utxo, block):
    # validate using n_workers "workers" on UTXO set utxo before block arrives.
    # Use the 'outputs first, then inputs' approach like it is proposed
    # for doing validation exploiting the DAG property.
    # The block is in the given order

    chunk_size = N_BLOCK // n_workers

    chunks = [block[i * chunk_size : (i+1) * chunk_size] for i in range(n_workers)]

    local_utxos=[]
    for chunk in chunks:
        local_utxos.append(OTI_Worker_processOutputs(utxo, chunk))

    for local_utxo, chunk in zip(local_utxos, chunks):
        OTI_Worker_processInputs(utxo, local_utxo, chunk)

    for local_utxo in local_utxos:
        OTI_Worker_Commit(utxo, local_utxo)

    for k in list(utxo.keys()):
        if utxo[k] == 0:
            del utxo[k]
    return utxo

def ValidateSequential(utxo, block):
    """ Simple sequential validation for code testing, no stats. """
    for txid, inputs, outputs in block:
        for inp in inputs:
            utxo[inp]-=1
            if utxo[inp] == 0:
                del utxo[inp]
        utxo[txid]=outputs
    return utxo

stats.clear()
utxo_val0=ValidateOutsThenIns(utxo0.copy(), block)
assert utxo_val0 == utxo_final
pp=pprint.PrettyPrinter(indent = 4)
print("Natural:")
pp.pprint(stats)

stats.clear()
utxo_val1=ValidateOutsThenIns(utxo0.copy(), sorted(block))
assert utxo_val1 == utxo_final
print("Lexicographic:")
pp.pprint(stats)
