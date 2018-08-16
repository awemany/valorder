A very simple exploration of validation order effects, by /u/awemany, 2018

Overview
--------

This is a minor exploration of the block (and maybe later also the
separate issue of memory pool ingress) validation order exploration
and issue demonstrations sing a very simple and incomplete python
model of the situation at hand.

This is by no means meant to be a detailed, "discrete event
simulation" style simulation of the validation process in the light of
the effect of inter-transactiondependencies.

This rather meant as a simple illustration of the issue that _I_ am
seeing and that I believe have simply not been sufficiently addressed
yet.  I also have the impression that there's a distinct sense of
'talking past each other' developing around this issue and therefore I
like to make things a bit more explicit.  It appears to me that
writing simple code for demonstration helps in this regard.

In my opinion as a consistent big blocker, we should still
proceed only *carefully* with changing Bitcoin!

Requirements: Python3 and numpy.

The code:
---------
There's three files:

`parameter.py`: Common parameters.

`generate.py`: Generate a stream of transactions and a ready made UTXO
set to explore block validation at the boundary. This one has to be called first.

`validate.py`: Explore the validation schemes, by validating the block
from the stream of transactions that has been generated above. Once
using natural order, and once using lexicographic order. Keep track of
the number of local and global read and write accesses.

Data structures
---------------
This is meant to be as simple as possible, so everything is ints
and tuples or lists of those.

### Transaction IDs
Are simple random integers.

### Transactions
Are triples of (txid, list of transaction IDs, num-output). With the meaning that the
first entry is the transaction id, the second entry are representing the input points
and the third entry the number of output points
of the transaction. The particular input or output in question is local data and
its details are not of further interest for this discussion, so dealing with this
has been left out.

### Blocks
A block is represented simply a linear list of transactions, just like in Bitcoin
right now.

As we're solely interested in the dynamics of the effects of transaction
ordering, details of the inner transaction structure are of course completely ignored.

Results
-------

Running with the given, completely arbitrary and thus also arbitrary
transaction generation parameters gives for example this result on my
host:

```
Natural:
Counter({'local_reads': 31949, 'local_writes': 29958, 'global_writes': 11991})
Lexicographic:
Counter({'local_reads': 43526, 'local_writes': 29958, 'global_writes': 23568})
```

which demonstrates that there *might* be ways to avoid costly traffic to
the global UTXO table. Note that these parameters here are creating highly
interdependent blocks.

Which is all which I like to point out with this. (So far)
