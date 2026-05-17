# Discovered Adventure Graph

```mermaid
flowchart TD
  R1[1: You are standing at the end of a road b...]
  R3[3: You are inside a building, a well house...]
  R4[4: You are in a valley in the forest besid...]
  R7[7: At your feet all the water of the strea...]
  R8[8: You are in a 20-foot depression floored...]
  R9[9: You are in a small chamber beneath a 3x...]
  R10[10: You are crawling over cobbles in a low...]
  R11[11: You are in a debris room filled with st...]
  R12[12: You are in an awkward sloping east/west...]
  R13[13: You are in a splendid chamber thirty fe...]
  R14[14: At your feet is a small pit breathing t...]
  R15[15: You are at one end of a vast hall stret...]

  %% Start room after bootstrap
  START((Start)) --> R3

  %% Discovered transitions
  R1 -->|e/in/enter| R3
  R1 -->|d/s| R4
  R3 -->|out/xyzzy/xyxxy/plugh/w/u| R1
  R3 -->|d/s| R4
  R4 -->|n| R1
  R4 -->|s/d| R7
  R7 -->|n| R4
  R7 -->|s| R8
  R8 -->|n| R7
  R8 -->|d/in/enter| R9
  R9 -->|out/u| R8
  R9 -->|w/in| R10
  R10 -->|e/out| R9
  R10 -->|in/w| R11
  R11 -->|e| R10
  R11 -->|w/u/in| R12
  R12 -->|e/d| R11
  R12 -->|w/u/in| R13
  R13 -->|e| R12
  R13 -->|w| R14
  R14 -->|e| R13
  R14 -->|d| R15
```

## Notes

- Graph reflects deterministic probes from a fresh process each time.
- Bootstrap commands: no, enter, take lamp, take keys, on, out.
- Candidate commands are prioritized from look context.
- Magic words (xyzzy/xyxxy/plugh) are included in probing.
- Increase --max-hops for broader exploration (runtime grows quickly).
