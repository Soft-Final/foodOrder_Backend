from .mail import send_password_async

def send_password(password: str, targets: list[str]) -> None:
    send_password_async.delay(password, targets)
