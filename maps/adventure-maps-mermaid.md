# Adventure 2.7 Map Model (Mermaid)

This document is a textual map model derived from the image maps in this folder.
It is intended to support deterministic route-based regression tests.

> **Viewing Mermaid Diagrams:**  
> Visual Studio's built-in Markdown preview does not render Mermaid diagrams. Options:
> - **GitHub**: View this file on GitHub for automatic Mermaid rendering
> - **VS Code**: Install [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)
> - **Online**: Copy diagram code to [mermaid.live](https://mermaid.live/)
> - **Alternative**: See GIF maps in the `maps/` directory

## Scope and Modeling Notes

- This model captures major rooms and explicit labeled links from map sheets 1-3.
- Dense maze regions are intentionally abstracted into grouped nodes.
- Cross-map connectors are represented as named portal nodes.

## Global Cross-Map Graph

```mermaid
flowchart TD
  M1_Building[Map 1 Building] <--> M2_Y2[Map 2 Y2]
  M1_EastHall[Map 1 East End Hall of Mists] <--> M2_EastHall[Map 2 East End Hall of Mists]
  M1_Bird[Map 1 Bird Chamber] <--> M2_Bird[Map 2 Bird Room]
  M2_LowNS[Map 2 Low N/S Passage] <--> M3_Dirty[Map 3 Dirty Passage]
  M2_SecretNS[Map 2 Secret N/S Canyon] <--> M3_Slab[Map 3 Slab Room]
  M2_SecretEW[Map 2 Secret E/W Canyon] --> M3_TightNS[Map 3 Tight N/S Canyon]
  M2_PloverRef[Map 2 Plover Ref] <--> M3_Plover[Map 3 Plover Room]
```

## Map 1 (Surface and Early Cave)

```mermaid
flowchart TD
  Road[End of Road]
  Building[Building]
  Hill[Hill]
  ForestVR[Forest by Valley and Road]
  Valley[Valley]
  ForestSide[Forest Valley on Side]
  Slit[Slit in Stream]
  OutsideGrate[Outside Grate]
  BelowGrate[Below Grate]
  Cobble[Cobble Crawl]
  Debris[Debris Room]
  BirdChamber[Bird Chamber]
  TopPit[Top of Pit]
  EastHallM1[East End Hall of Mists]

  Road -- enter --> Building
  Building -- out --> Road
  Road -- west --> Hill
  Hill -- east --> Road
  Road -- south --> Valley
  Valley -- west --> ForestVR
  ForestVR -- east --> Valley
  Valley -- south --> Slit
  Slit -- south --> OutsideGrate
  OutsideGrate -- down --> BelowGrate
  BelowGrate -- up --> OutsideGrate
  BelowGrate --- Cobble
  Cobble --- Debris
  Debris --- BirdChamber
  BirdChamber -- down --> TopPit
  TopPit -- up --> EastHallM1
```

## Map 2 (Main Cave, Halls, Chasms, Mazes)

```mermaid
flowchart TD
  Y2[Y2]
  Jumble[Jumble of Rocks]
  LowNS[Low N/S Passage]
  HallKing[Hall of Mt. King]
  SouthChamber[South Chamber]
  WestChamber[West Chamber]
  Circular[Circular Room]
  Division[Division in Passage]
  EastHall[East End Hall of Mists]
  WestHall[West End Hall of Mists]
  WestChasm[West Chasm]
  EastChasm[East Chasm]
  WideNS[Wide N/S Corridor]
  SmallCubical[Small Cubical]
  SmallChamber[Small Chamber]
  Nugget[Nugget Room]
  MazeCore[Maze Region (abstracted)]
  Brink[Brink of Pit]
  BirdRoom[Bird Room]

  Y2 <--> Jumble
  Y2 --- LowNS
  LowNS --- HallKing
  HallKing --- SouthChamber
  HallKing --- WestChamber
  HallKing --- Circular
  Circular --- Division
  Division --- EastHall
  EastHall --- Nugget
  EastHall --- SmallChamber
  Division --- WideNS
  WideNS --- SmallCubical
  WestHall --- WestChasm
  EastChasm --- EastHall
  WestChasm --- EastChasm
  WestHall --- MazeCore
  MazeCore --- Brink
  Brink --> BirdRoom
```

## Map 3 (Deep Cave and Canyon Links)

```mermaid
flowchart TD
  Dirty[Dirty Passage]
  BrinkClean[Brink of Clean Pit]
  BottomSmall[Bottom Small Pit]
  Witts[Witt's End]
  Dusty[Dusty Rocks]
  Complex[Complex Junction]
  Anteroom[Anteroom]
  Bedquilt[Bedquilt]
  Oriental[Oriental Room]
  Swiss[Swiss Cheese]
  Alcove[Alcove by Tight Tunnel]
  Plover[Plover Room]
  Slab[Slab Room]
  SecretNSRef[Map 2 Secret N/S Canyon]
  TightNS[Tight N/S Canyon]
  SecretEWRef[Map 2 Secret E/W Canyon]
  TwopitW[West End Twopit]
  TwopitE[East End Twopit]
  WesternPit[Western Pit]
  EasternPit[Eastern Pit]

  Dirty --- BrinkClean
  BrinkClean <--> BottomSmall
  BottomSmall --- Witts
  Dirty --- Dusty
  Dusty --- Complex
  Complex --- Anteroom
  Complex --- Bedquilt
  Bedquilt --- Oriental
  Oriental --- Swiss
  Swiss --- Alcove
  Alcove --- Plover
  Slab <--> SecretNSRef
  TightNS --> SecretEWRef
  TwopitW --- TwopitE
  TwopitW <--> WesternPit
  TwopitE <--> EasternPit
```

## Route Used for Regression

The regression test smoke.map1_surface_route follows this Map 1 route:

1. End of Road -> Building (enter)
2. Building -> End of Road (out)
3. End of Road -> Hill (west)
4. Hill -> End of Road/front of building (east)

This route verifies stable movement semantics across a small, map-backed cycle.
