# EventStream

Quick and dirty Tornado based rabbitmq consumer built with Bootstrap. 

### Why?

Fun to build and I needed something simple to display events which didn't really
fit into logs and graylog seemed a bit too hardcore for such a small project. 

### Installation

You will need a running kombu compatible amqp server. 

	virtualenv --no-site-packages env
	. env/bin/activate
	pip install -r requirements.txt
	python server.py


### Sending events

	See test_sender.py