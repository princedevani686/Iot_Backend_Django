import random
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from .models import DeviceData

class Command(BaseCommand):
    help = "Simulate device data"

    def handle(self, *args, **kwargs):
        for _ in range(10):  # Generate 10 iterations
            self.simulate_device_data(1, 'temperature')
            self.simulate_device_data(2, 'humidity')
            self.simulate_motion_data(4)
            time.sleep(60)  # Wait for 1 minute

    def simulate_device_data(self, device_id, data_type):
        value = random.uniform(20.0, 30.0) if data_type == "temperature" else random.uniform(40.0, 60.0)
        timestamp = datetime.now()
        DeviceData.objects.create(device_id=device_id, type=data_type, value=value, timestamp=timestamp)

    def simulate_motion_data(self, device_id):
        value = random.choice([0, 1])  # 0 = no motion, 1 = motion detected
        timestamp = datetime.now()
        DeviceData.objects.create(device_id=device_id, type="motion", value=value, timestamp=timestamp)
