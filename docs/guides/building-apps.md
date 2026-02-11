# Building Custom Apps with MOISSCode SDK

MOISSCode isn't just for the Sentinel Dashboard. You can embed the engine into your own Python applications.

## The SDK

The core engine is available as a Python package.

```python
from moisscode.interpreter import MOISSCodeInterpreter
from moisscode.parser import MOISSCodeParser
from moisscode.lexer import MOISSCodeLexer
```

## Example: Building a CLI Tool

Here is how you can build a simple command-line interface that executes MOISS protocols.

### 1. Define the Protocol

```moiss
protocol Triage {
    input: Patient p;
    if med.scores.qsofa(p) >= 1 {
        track p.lactate using KAE;
    }
}
```

### 2. Run the Engine

```python
# Initialize
interpreter = MOISSCodeInterpreter()

# Load Protocol
code = read_file("triage.moiss")

# Execute
events = interpreter.execute(parse(code))

# Handle Events
for e in events:
    if e['type'] == 'TRACK':
        print(f"Tracking {e['target']}: {e['value']}")
```

## Custom IO Handlers

You can override `med.io` to connect to real hardware.

```python
class RealDeviceManager:
    def connect(self, id, type):
        print(f"Connecting to physical {type} at {id}...")
        # WiFi / Bluetooth Logic Here
```
