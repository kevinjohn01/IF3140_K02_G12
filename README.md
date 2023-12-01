# IF3140_K02_G12


## CC Protocols Checklist

### Two-Phase Locking (2PL) ✅

### Optimistic Concurrency Control (OCC) ✅

### Multiversion Timestamp Ordering Concurrency Control (MVCC) ✅


## How to Run

Move to the src dir and run the following command,
```bash
{py|python|python3} main.py
```

## Testing

Test file structure

| Action | Transaction | Resource |
|-|-|-|
|R(Read), W(Write), C(Commit)|transaction number (e.g. 1, 22, 30)|alphabetic (A-Za-z) characters (e.g. A, AA, aB) or  assignment operation (e.g. A=5, B=9)| 

 > P.S. The default value of the resource is 0 

Example:
```
R 1 B
W 1 B=3 // make sure to not adding extra space between characters on the operation
R 2 A
W 2 A=3
R 2 B
W 1 B
W 2 A
C 1  // commit is optional
C 2
```

