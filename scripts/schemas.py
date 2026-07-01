from pydantic import BaseModel, Field
from typing import List, Optional

class ActuatorRow(BaseModel):
    enclosure_type: str = Field(description="Enclosure Type: Weatherproof or Explosionproof")
    voltage: str = Field(description="Operating voltage, e.g. 110V, 220V, 24V")
    phase: str = Field(description="Power phase: Single or 3-Phase")
    base_part_number: str = Field(description="Base part number code, e.g. 761A00-11300000/A")
    on_off_output_torque_in_lbs: Optional[float] = Field(None, description="On/Off Output Torque in In-Lbs.")
    on_off_output_torque_nm: Optional[float] = Field(None, description="On/Off Output Torque in Nm")
    on_off_duty_cycle_percent: Optional[int] = Field(None, description="On/Off Duty Cycle S4% percentage")
    on_off_cycles_per_hour: Optional[int] = Field(None, description="On/Off Cycles per Hour")
    modulating_output_torque_in_lbs: Optional[float] = Field(None, description="Modulating Output Torque in In-Lbs.")
    modulating_output_torque_nm: Optional[float] = Field(None, description="Modulating Output Torque in Nm")
    modulating_duty_cycle_percent: Optional[int] = Field(None, description="Modulating Duty Cycle S4% percentage")
    modulating_starts_per_hour: Optional[int] = Field(None, description="Modulating Starts per Hour")
    operating_speed_60hz_sec: Optional[float] = Field(None, description="Operating Speed (sec) 60 Hz")
    operating_speed_50hz_sec: Optional[float] = Field(None, description="Operating Speed (sec) 50 Hz")
    full_load_current_60hz_amps: Optional[float] = Field(None, description="Full Load Current (FLA) [A] 60 Hz")
    full_load_current_50hz_amps: Optional[float] = Field(None, description="Full Load Current (FLA) [A] 50 Hz")
    locked_rotor_current_60hz_amps: Optional[float] = Field(None, description="Locked Rotor Current (LRA) [A] 60 Hz")
    locked_rotor_current_50hz_amps: Optional[float] = Field(None, description="Locked Rotor Current (LRA) [A] 50 Hz")
    motor_power_watts: Optional[int] = Field(None, description="Motor Power Watts")


class ActuatorDataSet(BaseModel):
    actuators: List[ActuatorRow] = Field(description="List of all extracted actuators from the PDF tables")