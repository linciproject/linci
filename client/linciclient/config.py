#! /usr/bin/env python
#coding=utf-8

def main():
    from optparse import OptionParser
    import json
    import os
    from getpass import getpass

    parser = OptionParser()
    parser.add_option('--server-url', dest='server_url', default='http://localhost:8000/', help='linci server url, example: http://localhost:8000/')
    parser.add_option('--username', dest='username', default=None, help='username to login linci server')
    parser.add_option('--client-conf', dest='client_conf', default='./.linci_client.conf', help='linci client config file path, default is ./.linci_client.conf')

    options, args = parser.parse_args()
    d = {}
    if os.path.exists(options.client_conf):
        with open(options.client_conf) as f:
            d = json.load(f)
    server_url = options.server_url
    if server_url[-1]!='/':
        server_url = server_url + '/'
    d["server_url"] = server_url
    if options.username:
        d["username"] = options.username
        password = getpass("input the password:")
        d["password"] =  password
    with open(options.client_conf,"wb") as f:
        json.dump(d,f,indent=2)

if __name__ == '__main__':
    main()
