Credit to lots of people, but I am directly building off the KH2 AI research done by Govanify and Kenjiuno

## usage

python examples/lk_get_craw.bdx

creates "output.bdx", which is then loaded into a BAR file (using mod manager or manually)

To run it in an ARD event, create an event in evt.script that looks like this (the number after MapScript is the index of the bdx file in the BAR file. It looks like this will be placed at the end, so you can just count the number of files in the BAR + 1)

```
Program 0x0A
MapScript 9
AreaSettings 0 -1
	SetProgressFlag 0x281C
	SetEvent "204" Type 2
	SetPartyMenu 0
```

and here's an example of a mod.yml

```assets:
- method: binarc
  name: ard/hb04.ard
  source:
  - method: spawnpoint
    name: b_40
    source:
    - name: files\ard\hb04\b_40.yml
    type: AreaDataSpawn
  - method: spawnpoint
    name: b_80
    source:
    - name: files\ard\hb04\b_80.yml
    type: AreaDataSpawn
  - method: copy
    name: hb_l
    source:
    - name: files\ard\hb04\hb_last_laser.bdx
    type: Bdx
  - method: areadatascript
    name: evt
    source:
    - name: files\ard\hb04\test.areadatascript
    type: AreaDataScript
title: Randomizer Seed```

VERY LIMITED right now

Pretty much constrained just to calling functions with predefined integer arguments

See the list of functions (and how many arguments they take) here (everything starting with trap_)

https://kenjiuno.github.io/monitor-kh2fm/kh2ai

