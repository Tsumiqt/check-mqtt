# check-mqtt

A [Nagios]/[Icinga] plugin for checking connectivity to an [MQTT] broker.

## Configuration

Configuration is currently hard-coded in the Python source. Check the following variables and alter to taste:

```python
mqtt_host = 'localhost'
mqtt_port = 1883
mqtt_username = None
mqtt_password = None

check_topic = 'nagios/test'
check_payload = 'PiNG'
max_wait = 4
```

* `max_wait` is the time we're willing to wait for a SUB to the topic we PUBlish on.


 [nagios]: http://nagios.org
 [icinga]: http://icinga.org
 [mqtt]: http://mqtt.org
