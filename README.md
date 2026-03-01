# Cache Manager
### Tyler Schill
### Winter 2026

#### Overview
Written as part of an assignment for COSC 051 at Dartmouth, this
project simulates the logic behind how a cache operates. For
instance, it creates a cache filled with sets, within which
there are lines, and within those lines there are blocks with metadata.
It will then read a file line by line, with each line representing
a program touching a memory address. The program figures out if this
address is in the cache, and if is not, then it will either find
an empty line to put it in, or it will evict a line.

#### Eviction Behavior
Evict the line that was touched last (we keep track of when a line
was last touched in its metadata).

#### Supported Cache Structures
- Direct Mapped: 64 sets, 1 line each
- 2 Way Set Associative: 32 sets, 2 lines each
- 4 Way Set Associative: 16 sets, 4 lines each
- Fully Associative: 1 set, 64 lines
