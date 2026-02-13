"""
med.signal - Biosignal Processing Module for MOISSCode
Peak detection, heart rate variability, rhythm classification, SpO2 calculation,
and waveform analysis for medical device integration.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import math


class SignalEngine:
    """Biosignal processing engine for MOISSCode."""

    # ── Peak Detection ─────────────────────────────────────

    @staticmethod
    def detect_peaks(waveform: list, threshold: float = 0.5) -> dict:
        """
        Basic peak detection for ECG QRS complexes, pulse waveforms, etc.
        Uses threshold-based detection with refractory period.
        """
        waveform = [float(x) for x in waveform]
        threshold = float(threshold)
        n = len(waveform)

        if n < 3:
            return {'type': 'SIGNAL', 'error': 'Need >= 3 data points'}

        # Find max amplitude for relative threshold
        max_amp = max(abs(x) for x in waveform)
        abs_threshold = threshold * max_amp

        peaks = []
        refractory = max(3, n // 50)  # Minimum spacing between peaks

        i = 1
        while i < n - 1:
            if (waveform[i] > abs_threshold
                and waveform[i] > waveform[i-1]
                and waveform[i] >= waveform[i+1]):
                peaks.append({
                    'index': i,
                    'amplitude': round(waveform[i], 3)
                })
                i += refractory
            else:
                i += 1

        # Calculate intervals
        intervals = []
        for j in range(1, len(peaks)):
            intervals.append(peaks[j]['index'] - peaks[j-1]['index'])

        return {
            'type': 'SIGNAL_PEAKS',
            'total_samples': n,
            'peaks_detected': len(peaks),
            'peaks': peaks,
            'inter_peak_intervals': intervals,
            'threshold_used': round(abs_threshold, 3)
        }

    # ── Heart Rate ─────────────────────────────────────────

    @staticmethod
    def heart_rate_from_rr(rr_intervals_ms: list) -> dict:
        """
        Calculate heart rate from R-R intervals (in milliseconds).
        HR = 60000 / mean_RR_ms
        """
        rr = [float(x) for x in rr_intervals_ms]
        if not rr:
            return {'type': 'SIGNAL', 'error': 'No R-R intervals provided'}

        mean_rr = sum(rr) / len(rr)
        if mean_rr <= 0:
            return {'type': 'SIGNAL', 'error': 'Invalid R-R intervals'}

        hr = 60000.0 / mean_rr
        min_rr = min(rr)
        max_rr = max(rr)
        hr_max = 60000.0 / min_rr if min_rr > 0 else 0
        hr_min = 60000.0 / max_rr if max_rr > 0 else 0

        if hr < 60:
            classification = "BRADYCARDIA"
        elif hr <= 100:
            classification = "NORMAL_SINUS"
        elif hr <= 150:
            classification = "TACHYCARDIA"
        else:
            classification = "SEVERE_TACHYCARDIA"

        return {
            'type': 'SIGNAL_HR',
            'mean_hr_bpm': round(hr, 1),
            'min_hr_bpm': round(hr_min, 1),
            'max_hr_bpm': round(hr_max, 1),
            'mean_rr_ms': round(mean_rr, 1),
            'beats_analyzed': len(rr),
            'classification': classification
        }

    # ── Heart Rate Variability ─────────────────────────────

    @staticmethod
    def hrv_metrics(rr_intervals_ms: list) -> dict:
        """
        Heart Rate Variability (HRV) time-domain metrics.
        SDNN, RMSSD, pNN50 - standard HRV analysis.
        """
        rr = [float(x) for x in rr_intervals_ms]
        n = len(rr)

        if n < 5:
            return {'type': 'SIGNAL', 'error': 'Need >= 5 R-R intervals for HRV'}

        mean_rr = sum(rr) / n

        # SDNN: Standard deviation of NN (RR) intervals
        sdnn = math.sqrt(sum((x - mean_rr) ** 2 for x in rr) / (n - 1))

        # RMSSD: Root mean square of successive differences
        successive_diffs = [rr[i+1] - rr[i] for i in range(n - 1)]
        rmssd = math.sqrt(sum(d ** 2 for d in successive_diffs) / len(successive_diffs))

        # pNN50: Percentage of successive differences > 50 ms
        nn50 = sum(1 for d in successive_diffs if abs(d) > 50)
        pnn50 = 100 * nn50 / len(successive_diffs)

        # HRV interpretation
        if sdnn < 50:
            autonomic = "LOW_HRV"
            interpretation = "Reduced autonomic function - increased cardiac risk"
        elif sdnn < 100:
            autonomic = "MODERATE_HRV"
            interpretation = "Normal autonomic function"
        else:
            autonomic = "HIGH_HRV"
            interpretation = "Good autonomic function and cardiac health"

        return {
            'type': 'SIGNAL_HRV',
            'sdnn_ms': round(sdnn, 1),
            'rmssd_ms': round(rmssd, 1),
            'pnn50_pct': round(pnn50, 1),
            'mean_rr_ms': round(mean_rr, 1),
            'intervals_analyzed': n,
            'autonomic_status': autonomic,
            'interpretation': interpretation
        }

    # ── Rhythm Classification ──────────────────────────────

    @staticmethod
    def classify_rhythm(rr_intervals_ms: list) -> dict:
        """
        Basic cardiac rhythm classification from R-R intervals.
        Classifies: regular sinus, sinus brady/tachy, irregular, AF-like.
        """
        rr = [float(x) for x in rr_intervals_ms]
        n = len(rr)

        if n < 3:
            return {'type': 'SIGNAL', 'error': 'Need >= 3 intervals'}

        mean_rr = sum(rr) / n
        hr = 60000.0 / mean_rr if mean_rr > 0 else 0

        # Regularity: coefficient of variation of R-R intervals
        sd = math.sqrt(sum((x - mean_rr) ** 2 for x in rr) / (n - 1))
        cv = (sd / mean_rr * 100) if mean_rr > 0 else 0

        # Classification logic
        if cv < 10:
            regularity = "REGULAR"
        elif cv < 20:
            regularity = "MILDLY_IRREGULAR"
        else:
            regularity = "IRREGULAR"

        # Rhythm determination
        if regularity == "IRREGULAR" and cv > 25:
            rhythm = "ATRIAL_FIBRILLATION_SUSPECTED"
            action = "12-lead ECG recommended - possible AF"
        elif hr < 50:
            rhythm = "SINUS_BRADYCARDIA"
            action = "Evaluate symptoms, consider atropine if symptomatic"
        elif hr < 60:
            rhythm = "MILD_BRADYCARDIA"
            action = "Monitor, likely physiologic"
        elif hr <= 100:
            rhythm = "NORMAL_SINUS_RHYTHM"
            action = "No intervention needed"
        elif hr <= 150:
            rhythm = "SINUS_TACHYCARDIA"
            action = "Identify and treat underlying cause"
        else:
            rhythm = "SVT_POSSIBLE"
            action = "Consider vagal maneuvers, adenosine if SVT confirmed"

        return {
            'type': 'SIGNAL_RHYTHM',
            'rhythm': rhythm,
            'heart_rate': round(hr, 1),
            'regularity': regularity,
            'cv_percent': round(cv, 1),
            'action': action
        }

    # ── SpO2 Calculation ───────────────────────────────────

    @staticmethod
    def spo2_from_ratio(red_ac: float, red_dc: float,
                        ir_ac: float, ir_dc: float) -> dict:
        """
        Calculate SpO2 from pulse oximeter raw data.
        R = (Red_AC/Red_DC) / (IR_AC/IR_DC)
        SpO2 = 110 - 25 * R (Beer-Lambert approximation)
        """
        red_ac = float(red_ac)
        red_dc = float(red_dc)
        ir_ac = float(ir_ac)
        ir_dc = float(ir_dc)

        if red_dc == 0 or ir_dc == 0 or ir_ac == 0:
            return {'type': 'SIGNAL', 'error': 'DC or IR values cannot be zero'}

        r_ratio = (red_ac / red_dc) / (ir_ac / ir_dc)
        spo2 = 110 - 25 * r_ratio
        spo2 = max(0, min(100, spo2))

        if spo2 >= 95:
            status = "NORMAL"
        elif spo2 >= 90:
            status = "MILD_HYPOXEMIA"
        elif spo2 >= 85:
            status = "MODERATE_HYPOXEMIA"
        else:
            status = "SEVERE_HYPOXEMIA"

        return {
            'type': 'SIGNAL_SPO2',
            'spo2': round(spo2, 1),
            'r_ratio': round(r_ratio, 3),
            'status': status,
            'method': 'Beer-Lambert approximation'
        }

    # ── Waveform Analysis ──────────────────────────────────

    @staticmethod
    def moving_average(data: list, window: int = 5) -> dict:
        """
        Simple moving average filter for signal smoothing.
        Used to remove noise from biosignals.
        """
        data = [float(x) for x in data]
        window = int(window)
        n = len(data)

        if window < 1 or window > n:
            return {'type': 'SIGNAL', 'error': 'Invalid window size'}

        smoothed = []
        for i in range(n):
            start = max(0, i - window // 2)
            end = min(n, i + window // 2 + 1)
            smoothed.append(round(sum(data[start:end]) / (end - start), 3))

        return {
            'type': 'SIGNAL_FILTERED',
            'method': 'moving_average',
            'window': window,
            'input_length': n,
            'smoothed': smoothed
        }

    @staticmethod
    def detect_anomaly(data: list, baseline_mean: float = None,
                       threshold_sd: float = 2.0) -> dict:
        """
        Statistical anomaly detection in biosignal data.
        Flags data points exceeding threshold_sd standard deviations from baseline.
        """
        data = [float(x) for x in data]
        threshold_sd = float(threshold_sd)
        n = len(data)

        if n < 3:
            return {'type': 'SIGNAL', 'error': 'Need >= 3 data points'}

        if baseline_mean is None:
            baseline_mean = sum(data) / n
        else:
            baseline_mean = float(baseline_mean)

        sd = math.sqrt(sum((x - baseline_mean) ** 2 for x in data) / (n - 1))
        upper = baseline_mean + threshold_sd * sd
        lower = baseline_mean - threshold_sd * sd

        anomalies = []
        for i, val in enumerate(data):
            if val > upper or val < lower:
                anomalies.append({
                    'index': i,
                    'value': round(val, 3),
                    'deviation_sd': round(abs(val - baseline_mean) / sd, 1) if sd > 0 else 0,
                    'direction': 'HIGH' if val > upper else 'LOW'
                })

        return {
            'type': 'SIGNAL_ANOMALY',
            'baseline_mean': round(baseline_mean, 3),
            'sd': round(sd, 3),
            'threshold_sd': threshold_sd,
            'upper_limit': round(upper, 3),
            'lower_limit': round(lower, 3),
            'total_points': n,
            'anomalies_detected': len(anomalies),
            'anomalies': anomalies
        }

    # ── Respiratory Rate ───────────────────────────────────

    @staticmethod
    def respiratory_rate(waveform: list, sampling_rate_hz: float = 25.0) -> dict:
        """
        Estimate respiratory rate from impedance or chest waveform data.
        Uses zero-crossing method for simplicity.
        """
        waveform = [float(x) for x in waveform]
        sampling_rate_hz = float(sampling_rate_hz)
        n = len(waveform)

        if n < 10:
            return {'type': 'SIGNAL', 'error': 'Insufficient data for RR estimation'}

        # Remove DC offset
        mean_val = sum(waveform) / n
        centered = [x - mean_val for x in waveform]

        # Count zero crossings
        crossings = 0
        for i in range(1, n):
            if (centered[i-1] < 0 and centered[i] >= 0) or \
               (centered[i-1] >= 0 and centered[i] < 0):
                crossings += 1

        # Each full breath cycle = 2 crossings
        duration_sec = n / sampling_rate_hz
        cycles = crossings / 2.0
        rr = (cycles / duration_sec) * 60.0 if duration_sec > 0 else 0

        if rr < 12:
            status = "BRADYPNEA"
        elif rr <= 20:
            status = "NORMAL"
        elif rr <= 30:
            status = "TACHYPNEA"
        else:
            status = "SEVERE_TACHYPNEA"

        return {
            'type': 'SIGNAL_RR',
            'respiratory_rate': round(rr, 1),
            'duration_sec': round(duration_sec, 1),
            'cycles_detected': round(cycles, 1),
            'status': status
        }

    # ── Perfusion Index ────────────────────────────────────

    @staticmethod
    def perfusion_index(ac_component: float, dc_component: float) -> dict:
        """
        Calculate Perfusion Index (PI) from pulse oximeter data.
        PI = (AC / DC) * 100
        Normal PI > 1.0%, low perfusion < 0.5%
        """
        ac = float(ac_component)
        dc = float(dc_component)

        if dc == 0:
            return {'type': 'SIGNAL', 'error': 'DC component cannot be zero'}

        pi = (ac / dc) * 100

        if pi > 5:
            status = "STRONG_PERFUSION"
        elif pi > 1:
            status = "NORMAL_PERFUSION"
        elif pi > 0.5:
            status = "LOW_PERFUSION"
        else:
            status = "VERY_LOW_PERFUSION"

        return {
            'type': 'SIGNAL_PI',
            'perfusion_index': round(pi, 2),
            'status': status,
            'interpretation': 'Ratio of pulsatile to non-pulsatile blood flow'
        }
