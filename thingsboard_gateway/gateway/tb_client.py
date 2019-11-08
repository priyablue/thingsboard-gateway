#     Copyright 2019. ThingsBoard
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import logging
import time
from thingsboard_gateway.tb_client.tb_gateway_mqtt import TBGatewayMqttClient

log = logging.getLogger("tb_connection")


class TBClient:
    def __init__(self, config):
        self.__config = config
        self.__host = config["host"]
        self.__port = config.get("port", 1883)
        credentials = config["security"]
        self.__tls = False
        self.__ca_cert = None
        self.__private_key = None
        self.__cert = None
        self.__token = None
        if credentials.get("accessToken") is not None:
            self.__token = str(credentials["accessToken"])
        else:
            self.__tls = True
            self.__ca_cert = credentials.get("caCert")
            self.__private_key = credentials.get("privateKey")
            self.__cert = credentials.get("cert")
        self.client = TBGatewayMqttClient(self.__host, self.__port, self.__token, self)
        # Adding callbacks
        self.client._client._on_connect = self._on_connect
        self.client._client._on_disconnect = self._on_disconnect

    def is_connected(self):
        return self.client.is_connected

    def _on_connect(self, client, userdata, flags, rc, *extra_params):
        log.debug('Gateway connected to ThingsBoard')
        self.client._on_connect(client, userdata, flags, rc, *extra_params)

    def _on_disconnect(self, client, userdata, rc):
        log.info('Gateway disconnected.')

    def disconnect(self):
        self.client.disconnect()

    def connect(self, min_reconnect_delay=10):
        keep_alive = self.__config.get("keep_alive", 60)
        try:
            while not self.client.is_connected():
                log.debug("connecting to ThingsBoard")
                self.client.connect(tls=self.__tls,
                                    ca_certs=self.__ca_cert,
                                    cert_file=self.__cert,
                                    key_file=self.__private_key,
                                    keepalive=keep_alive,
                                    min_reconnect_delay=min_reconnect_delay)
                time.sleep(1)
        except Exception as e:
            log.exception(e)
            time.sleep(10)
