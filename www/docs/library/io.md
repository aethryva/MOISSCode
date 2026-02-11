---
sidebar_position: 12
title: med.io
---

# med.io — Device I/O

Interface for medical devices (pumps, ventilators, monitors) and laboratory information systems.

## Methods

### `connect_device(id, type)` → void
Register a device by ID and type.

### `command(id, cmd)` → dict
Send a command to a registered device.

### `infuse(pump_id, drug, rate)` → dict
Start an infusion on a pump.

### `get_lab(test)` → float
Fetch the latest result for a lab test.

## Example

```
med.io.connect_device("Pump_01", "InfusionPump");
med.io.infuse("Pump_01", "Norepinephrine", 0.1);
let lactate = med.io.get_lab("lactate");
```
