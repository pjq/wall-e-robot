import requests
import config
from lib.car_action import CarAction


def send_car_action(action: str):
    # R.id.stop -> carAction.action = "stop"
    # R.id.left -> carAction.action = "left"
    # R.id.right -> carAction.action = "right"
    # R.id.up -> carAction.action = "up"
    # R.id.down -> carAction.action = "down"

    car_action = CarAction()
    car_action.set_action(action)
    car_action.set_duration(1000)
    car_action.set_speed(30)
    car_action.set_angle(0)

    host = config.settings.car_api_url
    url = f"{host}/api/car/controller"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=car_action.to_dict(), headers=headers)
        if response.status_code == requests.codes.ok:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False


class CarController:
    ENDPOINT = "http://localhost:8000/car/action"
    HEADERS = {"Content-Type": "application/json"}

    @staticmethod
    def send_car_action(action: dict) -> bool:
        try:
            response = requests.post(url=CarController.ENDPOINT, json=action, headers=CarController.HEADERS)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False
