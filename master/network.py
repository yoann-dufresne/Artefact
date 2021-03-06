"""Communication between the master and the slaves.

Part of the master.
"""

import logging
import time
from threading import Thread
from collections import deque

import zmq


logger = logging.getLogger('root')


class MasterNetwork(Thread):
    """Network communication for the master."""

    def __init__(self):
        """Constructor for the class."""
        Thread.__init__(self)

        self.ctx = zmq.Context()
        self.poller = zmq.Poller()

        self._running = True
        logger.debug("new master network")

        self.configure_socket_from_slaves()
        self.configure_socket_to_slaves()

        self.messages_to_slaves = deque([])
        self.arduino_messages = deque([])
        self.status_messages = deque([])
        time.sleep(2)  # needed to wait for the slave slow connection
        self.socket_to_slaves.send_multipart([b"100", b"init"])

    def configure_socket_from_slaves(self):
        """Create ZMQ socket listening to the master."""
        self.socket_from_slaves = self.ctx.socket(zmq.SUB)
        self.socket_from_slaves.bind("tcp://0.0.0.0:5557")
        self.socket_from_slaves.setsockopt(zmq.SUBSCRIBE, b'')

        self.poller.register(self.socket_from_slaves, zmq.POLLIN)

    def configure_socket_to_slaves(self):
        self.socket_to_slaves = self.ctx.socket(zmq.PUB)
        self.socket_to_slaves.bind("tcp://0.0.0.0:5556")

    def run(self):
        """
        Run loop of the class.

        Send messages to master if any and listen to
        communications from the master (populating the inbox queue).

        We use a poller to get a timeout while listening,
        this way we can kill the loop and send messages without waiting for the next message.
        """
        while self._running:
            self.send_command()
            self.receive()
        logger.info("end NetworkCommunication")

    def stop(self):
        """Stop the main loop."""
        self._running = False

    def receive(self):
        """Receive messsages from slaves.

        We have two sockets, one for arduinos messages
        and one for slaves statuses (connections, error...)
        """
        sockets = dict(self.poller.poll(5))
        if not sockets:
            return

        msg = self.socket_from_slaves.recv_multipart()  # we only have one listening socket
        msg = [s.decode() for s in msg]

        logger.info("from arduinos -- message: {}".format(msg))

        # button from arduino
        try:
            device_id, message_string = msg
        except Exception as e:
            logger.error("Unknown message from arduino : {}".format(msg))
            logger.exception(e)
            return
        self.arduino_messages.append((device_id, message_string))

    def send_command(self):
        """Send a command to the slaves, with a channel and a message."""
        while self.messages_to_slaves:
            logger.info("message len before: {}".format(len(self.messages_to_slaves)))
            msg = self.messages_to_slaves.popleft()
            message = [s.encode() for s in msg]
            self.socket_to_slaves.send_multipart(message)
            logger.info("sending to arduinos : {}".format(message))
            logger.info("message len after: {}".format(len(self.messages_to_slaves)))
