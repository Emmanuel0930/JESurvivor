import os


class EmailNotifier:
    def enviar_confirmacion(self, reserva):
        print(f"Email REAL enviado para reserva {reserva.id}")


class MockNotifier:
    def enviar_confirmacion(self, reserva):
        print(f"Mock: confirmación de reserva {reserva.id}")


class NotificadorFactory:

    @staticmethod
    def crear():

        env = os.getenv("ENV_TYPE", "DEV")

        if env == "PROD":
            return EmailNotifier()
        else:
            return MockNotifier()