#!/usr/bin/env python

import logging
import functools
from Queue import Empty
import os.path
import collections

import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.template
import tornado.web
import tornado.websocket
from tornado.options import define, options

from kombu import BrokerConnection


define("port", default=8888, help="run on the given port", type=int)
define("refresh_rate", default=200, help="consume rabbitmq messages rate", type=int)
define("amqp", default="amqp://guest:guest@localhost:5672//",
    help="amqp connection string", type=str)


loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__),
    "templates"))


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/msgs", MessageHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__),
                "templates"),
            static_path=os.path.join(os.path.dirname(__file__),
                "static"),
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html",
            messages=MessageHandler.cache)


class MessageHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = collections.deque(maxlen=40)

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        MessageHandler.waiters.add(self)

    def on_close(self):
        MessageHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, event):
        cls.cache.appendleft(event)

    @classmethod
    def send_updates(cls, event):
        for waiter in cls.waiters:
            try:
                waiter.write_message(event)
            except:
                logging.error("Error sending message", exc_info=True)


def consume_messages(amqp_string):
    conn = BrokerConnection(amqp_string)
    queue = conn.SimpleQueue("eventstream")

    while True:
        try:
            message = queue.get(block=False, timeout=1)
        except Empty:
            break
        else:
            message.ack()
            pl = message.payload
            log_message = {
                'state': pl['state'],
                'state_msg': pl['state_msg'],
                'host': pl['host'],
                'body': pl['body'],
                'timestamp': pl['timestamp'],
                'html': loader.load("message.html").generate(message=pl)
            }
            MessageHandler.update_cache(log_message)
            MessageHandler.send_updates(log_message)

    queue.close()
    conn.close()


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    ioloop = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(functools.partial(consume_messages,
        options.amqp), options.refresh_rate, ioloop).start()
    ioloop.start()


if __name__ == "__main__":
    main()
