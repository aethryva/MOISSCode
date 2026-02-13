"""
med.io - Medical Device I/O Module for MOISSCode
Infusion pumps, patient monitors, ventilators, waveform capture, and alarm management.
"""

from typing import Dict, Any, List, Optional
import math
import random


class DeviceManager:
    """Driver interface for medical devices (Pumps, Ventilators, Monitors)."""

    def __init__(self):
        self.devices: Dict[str, Dict[str, Any]] = {}

    def register_device(self, device_id: str, device_type: str):
        self.devices[device_id] = {
            'type': device_type,
            'status': 'STANDBY',
            'params': {},
            'readings': {},
            'alarms': {},
            'log': []
        }

    def send_command(self, device_id: str, command: str, params: Dict[str, Any] = None):
        if device_id not in self.devices:
            return {"type": "ERROR", "msg": f"Device {device_id} not found"}

        self.devices[device_id]['status'] = command
        if params:
            self.devices[device_id]['params'].update(params)
        self.devices[device_id]['log'].append({
            'command': command, 'params': params
        })

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
    """Medical I/O - device and lab interface for MOISSCode."""
    devices = DeviceManager()
    lab = LabInterface()

    # ── Device Connection ──────────────────────────────────

    @staticmethod
    def connect_device(device_id: str, device_type: str):
        """Register and connect a medical device."""
        MedIO.devices.register_device(device_id, device_type)
        return {
            'type': 'IO_EVENT',
            'action': 'CONNECT',
            'device': device_id,
            'device_type': device_type,
            'status': 'CONNECTED'
        }

    @staticmethod
    def command(device_id: str, cmd: str):
        """Send a command to a device."""
        return MedIO.devices.send_command(device_id, cmd)

    # ── Infusion Pump Control ──────────────────────────────

    @staticmethod
    def infuse(pump_id: str, drug: str, rate: float):
        """Start or adjust an infusion on a pump."""
        rate = float(rate)
        MedIO.devices.send_command(pump_id, "RUN", {"drug": drug, "rate": rate})
        return {
            'type': 'IO_INFUSION',
            'pump': pump_id,
            'drug': drug,
            'rate': rate,
            'status': 'RUNNING'
        }

    @staticmethod
    def stop_infusion(pump_id: str):
        """Stop an infusion on a pump."""
        MedIO.devices.send_command(pump_id, "STOP", {})
        return {
            'type': 'IO_INFUSION',
            'pump': pump_id,
            'status': 'STOPPED'
        }

    @staticmethod
    def bolus(pump_id: str, drug: str, volume_ml: float, duration_min: float = 30):
        """Deliver a bolus dose."""
        volume_ml = float(volume_ml)
        duration_min = float(duration_min)
        rate = volume_ml / (duration_min / 60) if duration_min > 0 else volume_ml
        MedIO.devices.send_command(pump_id, "BOLUS", {
            "drug": drug, "volume_ml": volume_ml,
            "duration_min": duration_min, "rate_ml_hr": round(rate, 1)
        })
        return {
            'type': 'IO_BOLUS',
            'pump': pump_id,
            'drug': drug,
            'volume_ml': volume_ml,
            'duration_min': duration_min,
            'rate_ml_hr': round(rate, 1)
        }

    # ── Patient Monitor ────────────────────────────────────

    @staticmethod
    def read_monitor(monitor_id: str, parameter: str) -> dict:
        """
        Read a specific vital sign from a patient monitor.
        Parameters: HR, SpO2, RR, BP_SYS, BP_DIA, TEMP, ETCO2, CVP
        """
        # Simulated physiologic values with realistic noise
        sim_values = {
            'HR': 72 + random.gauss(0, 5),
            'SpO2': min(100, 97 + random.gauss(0, 1)),
            'RR': 16 + random.gauss(0, 2),
            'BP_SYS': 120 + random.gauss(0, 8),
            'BP_DIA': 75 + random.gauss(0, 5),
            'TEMP': 37.0 + random.gauss(0, 0.3),
            'ETCO2': 38 + random.gauss(0, 2),
            'CVP': 8 + random.gauss(0, 2),
        }

        param_upper = parameter.upper()
        value = sim_values.get(param_upper, None)

        if value is None:
            return {
                'type': 'IO_MONITOR',
                'monitor': monitor_id,
                'error': f'Unknown parameter: {parameter}'
            }

        value = round(value, 1)

        # Store in device readings
        if monitor_id in MedIO.devices.devices:
            MedIO.devices.devices[monitor_id]['readings'][param_upper] = value

        return {
            'type': 'IO_MONITOR',
            'monitor': monitor_id,
            'parameter': param_upper,
            'value': value
        }

    @staticmethod
    def read_all_vitals(monitor_id: str) -> dict:
        """Read all vital signs from a patient monitor."""
        params = ['HR', 'SpO2', 'RR', 'BP_SYS', 'BP_DIA', 'TEMP']
        vitals = {}
        for p in params:
            result = MedIO.read_monitor(monitor_id, p)
            vitals[p] = result.get('value', None)

        return {
            'type': 'IO_VITALS',
            'monitor': monitor_id,
            'vitals': vitals
        }

    # ── Ventilator Control ─────────────────────────────────

    @staticmethod
    def send_ventilator(vent_id: str, parameter: str, value: float) -> dict:
        """
        Set a ventilator parameter.
        Parameters: FiO2, PEEP, TV (tidal volume), RR, I_E_RATIO, MODE
        """
        value = float(value)
        MedIO.devices.send_command(vent_id, "SET", {parameter: value})
        return {
            'type': 'IO_VENTILATOR',
            'ventilator': vent_id,
            'parameter': parameter,
            'value': value,
            'status': 'SET'
        }

    @staticmethod
    def read_ventilator(vent_id: str) -> dict:
        """Read current ventilator settings and measured values."""
        settings = {
            'mode': 'AC/VC',
            'fio2': 0.4,
            'peep': 5,
            'tidal_volume_ml': 450,
            'set_rr': 14,
            'ie_ratio': '1:2',
            'measured_rr': 14 + random.gauss(0, 1),
            'measured_tv': 450 + random.gauss(0, 20),
            'peak_pressure': 22 + random.gauss(0, 2),
            'plateau_pressure': 18 + random.gauss(0, 1),
            'minute_ventilation': round(0.45 * 14, 1),
        }

        # Override with actual device params if connected
        if vent_id in MedIO.devices.devices:
            stored = MedIO.devices.devices[vent_id].get('params', {})
            settings.update(stored)

        return {
            'type': 'IO_VENTILATOR_READ',
            'ventilator': vent_id,
            'settings': settings
        }

    # ── Waveform Capture ───────────────────────────────────

    @staticmethod
    def read_waveform(device_id: str, channel: str,
                      duration_sec: float = 5.0,
                      sampling_rate_hz: float = 250.0) -> dict:
        """
        Capture waveform data from a device channel.
        Channels: ECG_II, PLETH, RESP, ABP
        Returns simulated waveform data.
        """
        duration_sec = float(duration_sec)
        sampling_rate_hz = float(sampling_rate_hz)
        n_samples = int(duration_sec * sampling_rate_hz)

        # Generate simulated waveform
        channel_upper = channel.upper()
        waveform = []

        for i in range(n_samples):
            t = i / sampling_rate_hz

            if channel_upper == 'ECG_II':
                # Simplified ECG-like waveform (QRS complex shape)
                phase = (t * 1.2) % 1.0  # ~72 bpm
                if 0.35 < phase < 0.40:
                    val = 1.5 * math.sin((phase - 0.35) * 20 * math.pi)
                else:
                    val = 0.05 * math.sin(2 * math.pi * t)
                val += random.gauss(0, 0.02)

            elif channel_upper == 'PLETH':
                # Pulse oximeter plethysmograph
                val = 0.5 * (1 + math.sin(2 * math.pi * 1.2 * t - math.pi/2))
                val += random.gauss(0, 0.01)

            elif channel_upper == 'RESP':
                # Respiratory impedance waveform
                val = math.sin(2 * math.pi * 0.25 * t)
                val += random.gauss(0, 0.05)

            elif channel_upper == 'ABP':
                # Arterial blood pressure waveform
                val = 90 + 30 * math.sin(2 * math.pi * 1.2 * t)
                val += 8 * math.sin(4 * math.pi * 1.2 * t)
                val += random.gauss(0, 1)

            else:
                val = random.gauss(0, 1)

            waveform.append(round(val, 4))

        return {
            'type': 'IO_WAVEFORM',
            'device': device_id,
            'channel': channel_upper,
            'duration_sec': duration_sec,
            'sampling_rate_hz': sampling_rate_hz,
            'samples': n_samples,
            'data': waveform
        }

    # ── Alarm Management ───────────────────────────────────

    @staticmethod
    def set_alarm(device_id: str, parameter: str,
                  low: float, high: float) -> dict:
        """Set alarm thresholds for a monitored parameter."""
        low = float(low)
        high = float(high)

        if device_id in MedIO.devices.devices:
            MedIO.devices.devices[device_id]['alarms'][parameter.upper()] = {
                'low': low, 'high': high
            }

        return {
            'type': 'IO_ALARM_SET',
            'device': device_id,
            'parameter': parameter,
            'low_threshold': low,
            'high_threshold': high
        }

    @staticmethod
    def check_alarms(device_id: str) -> dict:
        """Check all alarm conditions for a device."""
        if device_id not in MedIO.devices.devices:
            return {'type': 'IO_ALARM', 'error': f'Device {device_id} not found'}

        dev = MedIO.devices.devices[device_id]
        alarms = dev.get('alarms', {})
        readings = dev.get('readings', {})
        triggered = []

        for param, thresholds in alarms.items():
            if param in readings:
                val = readings[param]
                if val < thresholds['low']:
                    triggered.append({
                        'parameter': param,
                        'value': val,
                        'threshold': thresholds['low'],
                        'type': 'LOW'
                    })
                elif val > thresholds['high']:
                    triggered.append({
                        'parameter': param,
                        'value': val,
                        'threshold': thresholds['high'],
                        'type': 'HIGH'
                    })

        return {
            'type': 'IO_ALARM_CHECK',
            'device': device_id,
            'alarms_triggered': len(triggered),
            'triggered': triggered
        }

    # ── Lab Interface ──────────────────────────────────────

    @staticmethod
    def get_lab(test: str):
        """Read a lab result from the LIS interface."""
        return MedIO.lab.listen_for(test)
