#!/usr/bin/env python

# Copyright (c) 2013 Jan-Piet Mens <jpmens()gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of mosquitto nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import mosquitto
import ssl
import time
import sys
import os

mqtt_host = 'localhost'
mqtt_port = 1883
mqtt_username = None
mqtt_password = None

check_topic = 'nagios/test'
check_payload = 'PiNG'
max_wait = 4

status = 0
message = ''

nagios_codes = [ 'OK', 'WARNING', 'CRITICAL', 'UNKNOWN' ]

def on_connect(mosq, userdata, rc):
    mosq.subscribe(check_topic, 0)

def on_publish(mosq, userdata, mid):
    pass

def on_subscribe(mosq, userdata, mid, granted_qos):
    (res, mid) =  mosq.publish(check_topic, check_payload, qos=1, retain=False)

def on_message(mosq, userdata, msg):
    global message
    global status
    if str(msg.payload) == check_payload:
        userdata['have_response'] = True
        status = 0
        elapsed = (time.time() - userdata['start_time'])
        message = "PUB to %s at %s responded in %.2f" % (check_topic, mqtt_host, elapsed)

def on_disconnect(mosq, userdata, rc):
    exitus(1, "Unexpected disconnection. Incorrect credentials?")

def exitus(status=0, message="all is well"):
    print "%s - %s" % (nagios_codes[status], message)
    sys.exit(status)

userdata = {
    'have_response' : False,
    'start_time'    : time.time(),
}
mqttc = mosquitto.Mosquitto('nagios-%d' % (os.getpid()), clean_session=True, userdata=userdata)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

#mqttc.tls_set('root.ca',
#    cert_reqs=ssl.CERT_REQUIRED,
#    tls_version=1)

#mqttc.tls_set('root.ca', certfile='c1.crt', keyfile='c1.key', cert_reqs=ssl.CERT_REQUIRED, tls_version=3, ciphers=None)
#mqttc.tls_insecure_set(True)    # optional: avoid check certificate name if true

if mqtt_username is not None and mqtt_password is not None:
    mqttc.username_pw_set(mqtt_username, mqtt_password)

try:
    mqttc.connect(mqtt_host, mqtt_port, 60)
except Exception, e:
    status = 2
    message = "Connection to %s:%d failed: %s" % (mqtt_host, mqtt_port, str(e))
    exitus(status, message)

rc = 0
while userdata['have_response'] == False and rc == 0:
    rc = mqttc.loop()
    # print "loop rc=%d, have_response=%s" % (rc , userdata['have_response'])
    if time.time() - userdata['start_time'] > max_wait:
        message = 'timeout waiting for PUB'
        status = 2
        break

mqttc.disconnect()

exitus(status, message)

