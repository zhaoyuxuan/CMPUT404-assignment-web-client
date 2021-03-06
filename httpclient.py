#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        print(data)
        request_line = data.split("\r\n")[0]
        print(request_line)
        self.code = int(request_line.split(" ")[1])

        return self.code

    def get_headers(self, data):
        return None

    def get_body(self, data):
        self.body = data.split("\r\n\r\n")[1]

        return self.body

    def get_path(self, url_obj):
        if url_obj.path:
            return url_obj.path
        else:
            return "/"

    def get_port(self, url_obj):
        port = 80

        if url_obj.port:
            port = url_obj.port
        elif url_obj.scheme:
            if url_obj.scheme == 'http':
                port = 80

        return port

    def get_payload(self, data):
        return urllib.parse.urlencode(data)

    def get_payload_length(self, data):
        return len(data.encode('utf-8'))

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):

        url_obj = urllib.parse.urlparse(url)
        path = self.get_path(url_obj)
        port = self.get_port(url_obj)
        host = url_obj.netloc.split(":")[0]
        self.connect(host, port)

        reqeust_data = []
        reqeust_data.append("GET {} HTTP/1.1".format(path))
        reqeust_data.append("Host: {}".format(host))
        reqeust_data.append("Accept:  */*")
        reqeust_data.append("Connection: close")
        reqeust_data.append("\r\n")

        reqeust_header = "\r\n".join(reqeust_data)
        self.sendall(reqeust_header)
        print(reqeust_header)
        response_data = self.recvall(self.socket)
        code = self.get_code(response_data)
        body = self.get_body(response_data)
        print(response_data)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url_obj = urllib.parse.urlparse(url)
        path = self.get_path(url_obj)
        port = self.get_port(url_obj)
        host = url_obj.netloc.split(":")[0]
        self.connect(host, port)

        payload_body, content_length = None, 100
        if args:
            payload_body = self.get_payload(args)
            content_length = self.get_payload_length(payload_body)

        request_data = []
        request_data.append("POST {} HTTP/1.1".format(path))
        request_data.append("Host: {}".format(host))
        request_data.append("Content-Type: application/x-www-form-urlencoded")
        request_data.append("Content-Length: {}".format(content_length))
        request_data.append("Connection: close")
        request_data.append("\r\n")

        request_header = "\r\n".join(request_data)
        if payload_body:
            request_header += payload_body
        self.sendall(request_header)
        response_data = self.recvall(self.socket)
        code = self.get_code(response_data)
        body = self.get_body(response_data)
        print(body)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
