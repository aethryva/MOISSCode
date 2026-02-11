---
sidebar_position: 1
title: Getting Started
---

# Getting Started

MOISSCode is a domain-specific language for clinical decision support and biotech workflow automation.

## Prerequisites

- **Python 3.10+** — [Download Python](https://www.python.org/downloads/)
- **Git** — [Download Git](https://git-scm.com/downloads)

## Installation

```bash
git clone https://github.com/aethryva/MOISSCode.git
cd MOISSCode
```

**Windows (PowerShell):**
```powershell
py -m pip install -e .
```

**macOS / Linux:**
```bash
pip install -e .
```

## Your First Protocol

Create a file called `hello.moiss`:

```
protocol HelloMOISS {
    input: Patient p;

    let score = med.scores.qsofa(p);

    if score >= 2 {
        alert "High risk detected" severity: critical;
        administer Norepinephrine dose: 0.1 mcg/kg/min;
    } else {
        alert "Patient stable" severity: info;
    }

    assess p for sepsis;
}
```

Run it:

```bash
moiss run hello.moiss -v
```

## Validate Without Running

```bash
moiss validate hello.moiss
```

Output:
```
  ✅ Valid MOISSCode
     Protocols: 1  |  Types: 0  |  Functions: 0  |  Imports: 0
```

## Use from Python

```python
from moisscode import MOISSCodeLexer, MOISSCodeParser, MOISSCodeInterpreter

code = open('hello.moiss').read()
tokens = MOISSCodeLexer().tokenize(code)
program = MOISSCodeParser(tokens).parse_program()
events = MOISSCodeInterpreter().execute(program)

for e in events:
    print(e)
```

## What's Next?

- [Language Guide](/docs/language-guide) — Full syntax reference
- [Library Reference](/docs/library/overview) — All 13 medical modules
- [CLI](/docs/cli) — Command-line tool
