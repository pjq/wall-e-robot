import requests
from typing import Dict

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
    car_action.set_speed(50)
    car_action.set_angle(0)

    payload = car_action.to_dict()
    success = send_car_action(payload)
    if success:
        print("Car action sent successfully!")
    else:
        print("Error sending car action.")

    return success


def send_car_action(car_action: CarAction) -> bool:
    return send_car_action(car_action.to_dict())

def send_car_action(car_action: Dict) -> bool:
    host = config.settings.car_api_url
    url = f"{host}/api/car/controller"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=car_action, headers=headers)
        if response.status_code == requests.codes.ok:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

import requests

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
