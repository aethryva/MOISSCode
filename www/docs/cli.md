---
sidebar_position: 3
title: CLI
---

# Command-Line Interface

MOISSCode includes a CLI tool called `moiss`.

## Run a Protocol

```bash
moiss run protocol.moiss
```

With verbose event output:

```bash
moiss run protocol.moiss -v
```

## Validate Syntax

Parse-only validation (no execution):

```bash
moiss validate protocol.moiss
```

Output:
```
  ✅ Valid MOISSCode
     Protocols: 1  |  Types: 1  |  Functions: 2  |  Imports: 3
```

## Interactive REPL

Launch an interactive MOISSCode shell:

```bash
moiss repl
```

Type protocol blocks and statements line by line. The REPL executes when braces are balanced.

```
moiss> protocol Test {
  ...>     input: Patient p;
  ...>     let s = med.scores.qsofa(p);
  ...> }
  [1] LOG: [Protocol] Executing: Test
  [2] LOG: [Let] s = 3
```

Type `exit` or press `Ctrl+C` to quit.

## Version

```bash
moiss version
```

Output:
```
MOISSCode Engine v1.0.0-beta
Aethryva Deeptech
```
