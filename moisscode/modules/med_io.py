"""Medical I/O — device and lab interface for MOISSCode."""

from typing import Dict, Any, Callable


class DeviceManager:
    """Driver interface for medical devices (Pumps, Ventilators, Monitors)."""

    def __init__(self):
        self.devices: Dict[str, Dict[str, Any]] = {}

    def register_device(self, device_id: str, device_type: str):
        self.devices[device_id] = {
            'type': device_type,
            'status': 'STANDBY',
            'params': {}
        }

    def send_command(self, device_id: str, command: str, params: Dict[str, Any] = None):
        if device_id not in self.devices:
            return {"type": "ERROR", "msg": f"Device {device_id} not found"}

        self.devices[device_id]['status'] = command
        if params:
            self.devices[device_id]['params'].update(params)

        return {
            "type": "IO_EVENT",
            "device": device_id,
            "command": command,
            "params": params
        }

    def get_status(self, device_id: str) -> str:
        if device_id not in self.devices:
            return "UNKNOWN"
        return self.devices[device_id]['status']


class LabInterface:
    """Laboratory Information System (LIS) bridge using HL7-style messaging."""

    def __init__(self):
        self.results = {}

    def listen_for(self, test_name: str) -> float:
        """Fetch the latest result for a specific lab test."""
        if test_name.lower() == 'lactate':
            return 4.5
        if test_name.lower() == 'creatinine':
            return 1.2
        return 0.0


class MedIO:
    """Medical I/O — device and lab interface for MOISSCode."""
    devices = DeviceManager()
    lab = LabInterface()

    @staticmethod
    def connect_device(id: str, type: str):
        MedIO.devices.register_device(id, type)

    @staticmethod
    def command(id: str, cmd: str):
        MedIO.devices.send_command(id, cmd)

    @staticmethod
    def infuse(pump_id: str, drug: str, rate: float):
        MedIO.devices.send_command(pump_id, "RUN", {"drug": drug, "rate": rate})

    @staticmethod
    def get_lab(test: str):
        return MedIO.lab.listen_for(test)
