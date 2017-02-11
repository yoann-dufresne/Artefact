"""Main de test."""

from hardware.debug import Device as DebugDevice
from hardware.real import Device as RealDevice

from enigma import SwagEnigma, Enigma


def main(real=False):
    """main de test."""
    if real:
        device = RealDevice()
    else:
        device = DebugDevice()

    message = "swag 3 xxx..x.."
    se = SwagEnigma(message)  # SimonEnigma(device, 4, 3)

    e = Enigma()
    e.add_sub_enigma(se)

    if not real:
        device.webserver.button_trigger = e.button_triggered
        device.webserver._thread.join()


if __name__ == "__main__":
    print("===============================================")
    print("====== launching simulated device =============")
    main(real=False)
