"""Tests for med.signal - Biosignal Processing Module."""
import math
import pytest
from moisscode.modules.med_signal import SignalEngine


def test_detect_peaks_basic():
    waveform = [0, 0.1, 0.5, 1.0, 0.5, 0.1, 0, 0.1, 0.5, 1.0, 0.5, 0.1, 0]
    result = SignalEngine.detect_peaks(waveform, threshold=0.5)
    assert len(result["peaks"]) > 0

def test_detect_peaks_no_peaks():
    waveform = [0.1, 0.1, 0.1, 0.1]
    result = SignalEngine.detect_peaks(waveform, threshold=0.5)
    assert len(result["peaks"]) == 0

def test_heart_rate_from_rr_normal():
    result = SignalEngine.heart_rate_from_rr([750, 750, 750, 750])
    assert result["mean_hr_bpm"] == 80.0

def test_heart_rate_from_rr_tachy():
    result = SignalEngine.heart_rate_from_rr([400, 400, 400])
    assert result["mean_hr_bpm"] == 150.0

def test_hrv_metrics_returns_sdnn():
    rr = [800, 810, 790, 805, 795, 810, 790, 800]
    result = SignalEngine.hrv_metrics(rr)
    assert "sdnn_ms" in result
    assert "rmssd_ms" in result

def test_hrv_metrics_constant_rr():
    rr = [800, 800, 800, 800, 800]
    result = SignalEngine.hrv_metrics(rr)
    assert result["sdnn_ms"] < 1.0

def test_classify_rhythm_regular():
    rr = [800, 800, 800, 800, 800, 800]
    result = SignalEngine.classify_rhythm(rr)
    assert "rhythm" in result or "classification" in result

def test_classify_rhythm_tachy():
    rr = [400, 400, 400, 400, 400, 400]
    result = SignalEngine.classify_rhythm(rr)
    rhythm = result.get("rhythm", result.get("classification", ""))
    assert "TACHY" in rhythm.upper() or "SINUS" in rhythm.upper()

def test_spo2_from_ratio():
    result = SignalEngine.spo2_from_ratio(red_ac=0.8, red_dc=50.0,
                                          ir_ac=1.2, ir_dc=50.0)
    assert 85 < result["spo2"] < 100

def test_moving_average():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = SignalEngine.moving_average(data, window=3)
    assert len(result["smoothed"]) > 0

def test_detect_anomaly_with_outlier():
    data = [100, 101, 99, 100, 102, 200, 99, 100]
    result = SignalEngine.detect_anomaly(data, threshold_sd=2.0)
    assert len(result["anomalies"]) > 0

def test_detect_anomaly_clean():
    data = [100, 101, 100, 99, 100, 101]
    result = SignalEngine.detect_anomaly(data, threshold_sd=3.0)
    assert len(result["anomalies"]) == 0

def test_respiratory_rate():
    rr_hz = 0.25
    sr = 25.0
    waveform = [math.sin(2 * math.pi * rr_hz * i / sr) for i in range(200)]
    result = SignalEngine.respiratory_rate(waveform, sampling_rate_hz=sr)
    assert result["respiratory_rate"] > 0

def test_perfusion_index_normal():
    result = SignalEngine.perfusion_index(ac_component=2.0, dc_component=100.0)
    assert result["perfusion_index"] == 2.0

def test_perfusion_index_low():
    result = SignalEngine.perfusion_index(ac_component=0.3, dc_component=100.0)
    assert result["perfusion_index"] < 0.5
