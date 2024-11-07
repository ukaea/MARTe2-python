''' Import UDP Receiver and Sender all in one go '''

from martepy.marte2.datasources.udp.sender import UDPSender
from martepy.marte2.datasources.udp.receiver import UDPReceiver

__all__ = [
        'UDPSender',
        'UDPReceiver',
]
