from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import csv
from enum import Enum
from pathlib import Path

class IncidentType(Enum):
    ACCIDENT = "Accident"
    ROADWORK = "Road Work"
    CLOSURE = "Road Closure"

@dataclass
class TrafficIncident:
    scats_number: int
    incident_type: IncidentType
    start_time: datetime
    duration: timedelta  # in hours
    severity: float  # 0.0 to 1.0, affects traffic flow multiplier
    description: str

class IncidentSimulator:
    def __init__(self, network_file: str):
        self.scats_locations = []
        self.active_incidents = []
        self._load_scats_locations(network_file)

    def _load_scats_locations(self, network_file: str):
        with open(network_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.scats_locations.append(int(row['SCATS Number']))

    def generate_random_incident(self, current_time: datetime) -> TrafficIncident:
        incident_type = random.choice(list(IncidentType))
        scats_number = random.choice(self.scats_locations)
        
        # Generate duration based on incident type
        if incident_type == IncidentType.ACCIDENT:
            duration = timedelta(hours=random.uniform(0.5, 3))
            severity = random.uniform(0.5, 1.0)
            description = f"Traffic accident at intersection {scats_number}"
        elif incident_type == IncidentType.ROADWORK:
            duration = timedelta(hours=random.uniform(2, 8))
            severity = random.uniform(0.3, 0.7)
            description = f"Road work at intersection {scats_number}"
        else:  # CLOSURE
            duration = timedelta(hours=random.uniform(1, 6))
            severity = 1.0
            description = f"Road closure at intersection {scats_number}"

        return TrafficIncident(
            scats_number=scats_number,
            incident_type=incident_type,
            start_time=current_time,
            duration=duration,
            severity=severity,
            description=description
        )

    def get_active_incidents(self, current_time: datetime) -> list[TrafficIncident]:
        # Remove expired incidents
        self.active_incidents = [
            incident for incident in self.active_incidents 
            if incident.start_time + incident.duration > current_time
        ]
        return self.active_incidents

    def add_incident(self, incident: TrafficIncident):
        self.active_incidents.append(incident)

    def get_flow_multiplier(self, scats_number: int, current_time: datetime) -> float:
        """Returns a multiplier (0.0 to 1.0) to adjust traffic flow based on active incidents"""
        active_incidents = self.get_active_incidents(current_time)
        multiplier = 1.0

        for incident in active_incidents:
            if incident.scats_number == scats_number:
                # Reduce the multiplier based on incident severity
                multiplier *= (1.0 - incident.severity)

        return max(0.1, multiplier)  # Ensure flow doesn't go below 10% of normal

# Create a global instance of the simulator
TRAFFIC_NETWORK_FILE = str(Path(__file__).parent.parent / 'data' / 'traffic_network2.csv')
incident_simulator = IncidentSimulator(TRAFFIC_NETWORK_FILE)
