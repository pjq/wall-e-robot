class CarAction:
    SUPPORTED_ACTIONS = ("stop", "left", "right", "up", "down")

    def __init__(self):
        self.action = ""
        self.duration = 0
        self.speed = 0
        self.angle = 0

    def set_action(self, action: str) -> None:
        if action not in self.SUPPORTED_ACTIONS:
            # raise ValueError(f"Unsupported action: {action}")
            action="stop"

        self.action = action

    def set_duration(self, duration: int) -> None:
        self.duration = duration

    def set_speed(self, speed: int) -> None:
        self.speed = speed

    def set_angle(self, angle: int) -> None:
        self.angle = angle

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "duration": self.duration,
            "speed": self.speed,
            "angle": self.angle
        }
