#!/usr/bin/env python

import datetime
import time
import random
import socket

from kombu import BrokerConnection


bootstrap_labels = ['success', 'warning', 'important', 'info']


def main():
    conn = BrokerConnection("amqp://guest:guest@localhost:5672//")
    queue = conn.SimpleQueue("eventstream")
    queue_options = {'serializer': 'json', 'compression': 'zlib'}

    host = socket.gethostname()

    while True:
        queue.put({
            'state': random.choice(bootstrap_labels),
            'state_msg': 'Hello',
            'host': host,
            'timestamp': datetime.datetime.now().isoformat(),
            'body': 'foobar'}, **queue_options)
        time.sleep(random.random() / 8.0)

    queue.close()
    conn.close()


if __name__ == "__main__":
    main()
