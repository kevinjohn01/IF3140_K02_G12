# IF3140_K02_G12


## CC Protocols

### Two-Phase Locking (2PL)
### Optimistic Concurrency Control (OCC)
Using serial validation based OCC without threading.
### Multiversion Timestamp Ordering Concurrency Control (MVCC)

## How to Run

Move to the src dir and run the following command,
```bash
{py|python|python3} main.py
```

## Test

Test file structure

| Action | Transaction | Resource | Operation |
|-|-|-|-|
|R(Read), W(Write), C(Commit), O(Operation)|transaction number (e.g. 1, 22, 30)|A, B, C|set resource to a specific numberic value (e.g. A=5, B=9)|

 > P.S. The default value of the resource is 0 

Example:
```
R 1 B
O 1 B=3 // make sure to not adding extra space between characters on the operation
R 2 A
O 2 A=3
R 2 B
W 1 B
W 2 A
C 1  // commit is optional
C 2
```

