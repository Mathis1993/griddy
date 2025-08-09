import json
import logging

from electric_cars.models import Car


class CarImporter:
    logger = logging.getLogger(__name__)

    def __init__(self, path: str):
        file = open(path, "rb")
        data = file.read()
        file.close()
        self.json_obj = json.loads(data)

    def import_cars(self):
        cars = []
        for car_data in self.json_obj:
            vehicle_id = car_data.get("Vehicle_ID")
            model = car_data.get("Vehicle_Model")
            make = car_data.get("Vehicle_Make")
            model_version = car_data.get("Vehicle_Model_Version")
            model_year = car_data.get("Availability_Date_From", "").split("-")[-1]
            battery_capacity = car_data.get("Battery_Capacity_Full")

            if not (model and make and battery_capacity):
                self.logger.warning(f"Missing data for car with ID {vehicle_id}")
                continue

            car = Car(
                model=model,
                make=make,
                model_version=model_version,
                model_year=model_year,
                battery_capacity_kwh=battery_capacity,
            )

            car_name = car.__str__()
            if car_name in [car.__str__() for car in cars]:
                continue

            cars.append(car)

        self.logger.info(f"Creating {len(cars)} car entities.")
        Car.objects.bulk_create(cars)
