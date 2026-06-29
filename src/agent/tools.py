import os
import sqlite3
from typing import Optional
from langchain_core.tools import tool

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "electric_data_table.db")

#TOOL 1:
@tool
def query_by_part_number(part_number: str) -> str:
    """
    Consults the database to retrieve all technical specifications of a specific actuator 
    using its exact base part number. Use this tool when the user mentions a specific model code.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    clean_part_number = part_number.strip().replace("*", "")

    query = 'SELECT * FROM electric_data_table WHERE "Base Part Number" LIKE ?'
    cursor.execute(query, (f"%{clean_part_number}%",))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No actuator found for part number: {part_number}"

    return str([dict(row) for row in rows])


#TOOL 2:
@tool
def query_by_spects(
    enclosure_type: Optional[str] = None,
    voltage: Optional[str] = None,
    phase: Optional[str] = None,
    min_on_off_torque: Optional[float] = None,
    min_modulating_torque: Optional[int] = None,
    max_speed_seconds: Optional[int] = None,
    motor_power: Optional[int] = None
) -> str:
    """
    Search and filter the actuators database based on strict engineering requirements.

    Args:
        enclosure_type: 'Weatherproof' or 'Explosionproof'.
        voltage: Operating voltage, e.g., '110V', '220V', '24V'.
        phase: Electrical phase number, typical values are 1 or 3.
        min_on_off_torque: Minimum required torque for On/Off operation (Nm).
        min_modulating_torque: Minimum required torque for Modulating operation (Nm).
        max_speed_seconds: Maximum acceptable operating time to open/close (seconds).
        motor_power: Minimum required motor power in watts.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM electric_data_table WHERE 1=1"
    params = []

    if enclosure_type:
        query += ' AND "Enclosure Type" = ?'
        params.append(enclosure_type)

    if voltage:
        query += ' AND "Voltage" = ?'
        params.append(voltage)

    if phase is not None:
        query += ' AND "Phase" = ?'
        params.append(phase)

    if min_on_off_torque is not None:
        query += ' AND "On/Off Output Torque Nm" >= ?'
        params.append(min_on_off_torque)

    if min_modulating_torque is not None:
        query += ' AND "Modulating Output Torque Nm" >= ?'
        params.append(min_modulating_torque)

    if max_speed_seconds is not None:
        # Match actuators that are equal or faster (lower seconds) than requested.
        query += ' AND "Operating Speed (sec) 60 Hz" <= ?'
        params.append(max_speed_seconds)

    if motor_power is not None:
        query += ' AND "Motor Power Watts" >= ?'
        params.append(motor_power)

    query += " LIMIT 5"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No actuators found matching the specified filters."

    return str([dict(row) for row in rows])

tools = [query_by_part_number, query_by_spects]