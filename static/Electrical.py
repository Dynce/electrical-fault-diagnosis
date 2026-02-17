"""
Electrical Fault Diagnosis System
This module provides utilities for diagnosing electrical faults in systems.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple
import math


class FaultType(Enum):
    """Enumeration of electrical fault types"""
    SHORT_CIRCUIT = "Short Circuit"
    OPEN_CIRCUIT = "Open Circuit"
    GROUND_FAULT = "Ground Fault"
    PHASE_IMBALANCE = "Phase Imbalance"
    OVERVOLTAGE = "Overvoltage"
    UNDERVOLTAGE = "Undervoltage"
    OVERCURRENT = "Overcurrent"
    HARMONIC_DISTORTION = "Harmonic Distortion"
    POWER_FACTOR_LOW = "Low Power Factor"
    NONE = "No Fault"


@dataclass
class ElectricalReading:
    """Data class for electrical measurements"""
    voltage: float  # in volts
    current: float  # in amperes
    frequency: float  # in Hz
    power_factor: float  # 0.0 to 1.0
    phase_a: float  # Phase A voltage
    phase_b: float  # Phase B voltage
    phase_c: float  # Phase C voltage
    temperature: float  # in Celsius


class FaultDiagnosis:
    """Main class for electrical fault diagnosis"""
    
    # Threshold values
    VOLTAGE_MIN = 200  # V
    VOLTAGE_MAX = 250  # V
    CURRENT_MAX = 30  # A
    FREQUENCY_MIN = 48  # Hz
    FREQUENCY_MAX = 52  # Hz
    POWER_FACTOR_MIN = 0.85
    PHASE_IMBALANCE_MAX = 5  # percentage
    TEMPERATURE_MAX = 80  # Celsius
    
    def __init__(self):
        """Initialize the fault diagnosis system"""
        self.fault_history: List[Tuple[str, FaultType]] = []
        self.threshold_violations = []
    
    def diagnose(self, reading: ElectricalReading) -> Dict:
        """
        Diagnose faults based on electrical readings
        
        Args:
            reading: ElectricalReading object with measurements
            
        Returns:
            Dictionary containing diagnosis results
        """
        faults = []
        details = []
        
        # Check for voltage faults
        voltage_fault = self._check_voltage(reading.voltage)
        if voltage_fault:
            faults.append(voltage_fault)
            details.append(f"Voltage: {reading.voltage}V (Normal: {self.VOLTAGE_MIN}-{self.VOLTAGE_MAX}V)")
        
        # Check for current faults
        current_fault = self._check_current(reading.current)
        if current_fault:
            faults.append(current_fault)
            details.append(f"Current: {reading.current}A (Max: {self.CURRENT_MAX}A)")
        
        # Check for frequency faults
        frequency_fault = self._check_frequency(reading.frequency)
        if frequency_fault:
            faults.append(frequency_fault)
            details.append(f"Frequency: {reading.frequency}Hz (Normal: {self.FREQUENCY_MIN}-{self.FREQUENCY_MAX}Hz)")
        
        # Check for power factor faults
        pf_fault = self._check_power_factor(reading.power_factor)
        if pf_fault:
            faults.append(pf_fault)
            details.append(f"Power Factor: {reading.power_factor:.2f} (Min: {self.POWER_FACTOR_MIN})")
        
        # Check for three-phase imbalance
        imbalance_fault = self._check_phase_imbalance(reading.phase_a, reading.phase_b, reading.phase_c)
        if imbalance_fault:
            faults.append(imbalance_fault)
            details.append(f"Phase Imbalance detected: A={reading.phase_a:.1f}V, B={reading.phase_b:.1f}V, C={reading.phase_c:.1f}V")
        
        # Check for temperature
        temp_fault = self._check_temperature(reading.temperature)
        if temp_fault:
            faults.append(temp_fault)
            details.append(f"Temperature: {reading.temperature}°C (Max: {self.TEMPERATURE_MAX}°C)")
        
        # Determine primary fault
        primary_fault = faults[0] if faults else FaultType.NONE
        severity = self._calculate_severity(reading, faults)
        
        return {
            "primary_fault": primary_fault.value,
            "all_faults": [f.value for f in faults],
            "severity": severity,
            "confidence": self._calculate_confidence(reading),
            "details": details,
            "action": self._recommend_action(primary_fault)
        }
    
    def _check_voltage(self, voltage: float) -> FaultType or None:
        """Check for voltage-related faults"""
        if voltage > self.VOLTAGE_MAX:
            return FaultType.OVERVOLTAGE
        elif voltage < self.VOLTAGE_MIN:
            return FaultType.UNDERVOLTAGE
        return None
    
    def _check_current(self, current: float) -> FaultType or None:
        """Check for overcurrent faults"""
        if current > self.CURRENT_MAX:
            return FaultType.OVERCURRENT
        return None
    
    def _check_frequency(self, frequency: float) -> FaultType or None:
        """Check for frequency abnormalities"""
        if frequency < self.FREQUENCY_MIN or frequency > self.FREQUENCY_MAX:
            return FaultType.HARMONIC_DISTORTION
        return None
    
    def _check_power_factor(self, power_factor: float) -> FaultType or None:
        """Check for power factor issues"""
        if power_factor < self.POWER_FACTOR_MIN:
            return FaultType.POWER_FACTOR_LOW
        return None
    
    def _check_phase_imbalance(self, va: float, vb: float, vc: float) -> FaultType or None:
        """Check for three-phase voltage imbalance"""
        avg_voltage = (va + vb + vc) / 3
        if avg_voltage == 0:
            return None
        
        imbalance_a = abs((va - avg_voltage) / avg_voltage) * 100
        imbalance_b = abs((vb - avg_voltage) / avg_voltage) * 100
        imbalance_c = abs((vc - avg_voltage) / avg_voltage) * 100
        
        max_imbalance = max(imbalance_a, imbalance_b, imbalance_c)
        
        if max_imbalance > self.PHASE_IMBALANCE_MAX:
            return FaultType.PHASE_IMBALANCE
        return None
    
    def _check_temperature(self, temperature: float) -> FaultType or None:
        """Check for overtemperature"""
        if temperature > self.TEMPERATURE_MAX:
            return FaultType.OVERCURRENT  # Usually caused by overcurrent
        return None
    
    def _calculate_severity(self, reading: ElectricalReading, faults: List[FaultType]) -> str:
        """Calculate fault severity level"""
        if not faults or FaultType.NONE in faults:
            return "None"
        
        if len(faults) >= 3:
            return "Critical"
        
        severity_map = {
            FaultType.SHORT_CIRCUIT: "Critical",
            FaultType.GROUND_FAULT: "Critical",
            FaultType.OVERCURRENT: "High",
            FaultType.OVERVOLTAGE: "High",
            FaultType.PHASE_IMBALANCE: "Medium",
            FaultType.POWER_FACTOR_LOW: "Low",
        }
        
        for fault in faults:
            if fault in severity_map:
                return severity_map[fault]
        
        return "Medium"
    
    def _calculate_confidence(self, reading: ElectricalReading) -> float:
        """Calculate confidence level of diagnosis (0-100%)"""
        confidence = 100.0
        
        # Reduce confidence if readings are at extremes
        if reading.voltage > self.VOLTAGE_MAX * 1.5 or reading.voltage < self.VOLTAGE_MIN * 0.5:
            confidence -= 10
        
        if reading.current > self.CURRENT_MAX * 1.5:
            confidence -= 10
        
        if reading.power_factor < 0.7:
            confidence -= 15
        
        return max(0, min(100, confidence))
    
    def _recommend_action(self, fault: FaultType) -> str:
        """Recommend corrective action based on fault type"""
        actions = {
            FaultType.SHORT_CIRCUIT: "IMMEDIATE ACTION: Isolate circuit and check for damaged wiring or components.",
            FaultType.OPEN_CIRCUIT: "Check continuity and repair broken connections.",
            FaultType.GROUND_FAULT: "Isolate system and test insulation resistance. Repair grounding issues.",
            FaultType.PHASE_IMBALANCE: "Check load distribution across phases and rebalance if necessary.",
            FaultType.OVERVOLTAGE: "Check voltage regulator and power supply settings.",
            FaultType.UNDERVOLTAGE: "Verify power supply and transformer settings.",
            FaultType.OVERCURRENT: "Reduce load or check for short circuits. Verify circuit breaker rating.",
            FaultType.HARMONIC_DISTORTION: "Install harmonic filters or upgrade power quality equipment.",
            FaultType.POWER_FACTOR_LOW: "Install power factor correction capacitors.",
            FaultType.NONE: "System operating normally.",
        }
        
        return actions.get(fault, "Perform maintenance inspection.")
    
    def calculate_power(self, voltage: float, current: float, power_factor: float) -> float:
        """Calculate real power in Watts"""
        return voltage * current * power_factor
    
    def calculate_apparent_power(self, voltage: float, current: float) -> float:
        """Calculate apparent power in Volt-Amperes"""
        return voltage * current
    
    def calculate_reactive_power(self, voltage: float, current: float, power_factor: float) -> float:
        """Calculate reactive power in Volt-Amperes Reactive"""
        sin_phi = math.sqrt(1 - power_factor ** 2)
        return voltage * current * sin_phi


def create_sample_reading() -> ElectricalReading:
    """Create a sample electrical reading for testing"""
    return ElectricalReading(
        voltage=230.0,
        current=15.5,
        frequency=50.0,
        power_factor=0.92,
        phase_a=230.5,
        phase_b=229.8,
        phase_c=230.2,
        temperature=45.5
    )

http://127.0.0.1:5000
or
http://10.12.2.51:5000