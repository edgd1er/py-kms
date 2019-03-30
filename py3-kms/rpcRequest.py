#!/usr/bin/env python3

import binascii
import logging

from dcerpc import MSRPCRequestHeader, MSRPCRespHeader
import kmsBase
import rpcBase
from formatText import justify, shell_message, byterize

logger = logging.getLogger('root')

class handler(rpcBase.rpcBase):
        def parseRequest(self):
                request = MSRPCRequestHeader(self.data)
                shell_message(nshell = 14)
                request = byterize(request)
                logger.debug("RPC Message Request Bytes: \n%s\n" % justify(binascii.b2a_hex(self.data).decode('utf-8')))
                logger.debug("RPC Message Request: \n%s\n" % justify(request.dump(print_to_stdout = False)))
                                
                return request

        def generateResponse(self, request):
                responseData = kmsBase.generateKmsResponseData(request['pduData'], self.config)
                envelopeLength = len(responseData)

                response = MSRPCRespHeader()
                response['ver_major'] = request['ver_major']
                response['ver_minor'] = request['ver_minor']
                response['type'] = self.packetType['response']
                response['flags'] = self.packetFlags['firstFrag'] | self.packetFlags['lastFrag']
                response['representation'] = request['representation']
                response['call_id'] = request['call_id']

                response['alloc_hint'] = envelopeLength
                response['ctx_id'] = request['ctx_id']
                response['cancel_count'] = 0

                response['pduData'] = responseData

                shell_message(nshell = 17)
                response = byterize(response)
                logger.debug("RPC Message Response: \n%s\n" % justify(response.dump(print_to_stdout = False)))
                logger.debug("RPC Message Response Bytes: \n%s\n" % justify(binascii.b2a_hex(str(response).encode('latin-1')).decode('utf-8')))
                
                return response

        def generateRequest(self):
                request = MSRPCRequestHeader()

                request['ver_major'] = 5
                request['ver_minor'] = 0
                request['type'] = self.packetType['request']
                request['flags'] = self.packetFlags['firstFrag'] | self.packetFlags['lastFrag']
                request['representation'] = 0x10
                request['call_id'] = self.config['call_id']
                request['alloc_hint'] = len(self.data)
                request['pduData'] = str(self.data)

                shell_message(nshell = 11)
                request = byterize(request)
                logger.debug("RPC Message Request: \n%s\n" % justify(request.dump(print_to_stdout = False)))
                logger.debug("RPC Message Request Bytes: \n%s\n" % justify(binascii.b2a_hex(str(request).encode('latin-1')).decode('utf-8')))
                
                return request

        def parseResponse(self):
                return response
