"""Message encryption module"""
import os
import sys
import logging
import base64
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Hash import SHA1
from common.decos import Logging

LOGGER = logging.getLogger('client')


class EncryptDecrypt:
    HASH_FUNCTION = SHA1
    HASH_SIZE = SHA1.digest_size  # SHA1 Hash size in bytes
    KEY_SIZE = 2048  # RSA Key size in bits
    INPUT_BLOCK_SIZE = int(KEY_SIZE / 8 - 2 * HASH_SIZE - 2)
    OUTPUT_BLOCK_SIZE = 256  # Encrypted block key plus encrypted block

    """The class creates keys, encodes and decodes messages"""
    def __init__(self, user_login):
        """Get keys, create object - decoder"""
        self.keys = self._get_keys(user_login)
        self.decrypter = PKCS1_OAEP.new(self.keys)
        self.current_encrypt = None

    @Logging()
    def _get_keys(self, user_login):
        """Function create new keys or import from file"""

        #  for cx-Freeze - exe file
        if getattr(sys, 'frozen', False):
            dir_path = os.path.dirname(sys.executable)
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__))

        file_path = os.path.join(dir_path, f'{user_login}.key')
        if not os.path.exists(file_path):
            keys = RSA.generate(self.KEY_SIZE, os.urandom)
            with open(file_path, 'wb') as file:
                file.write(keys.export_key())
        else:
            with open(file_path, 'rb') as file:
                keys = RSA.import_key(file.read())
        return keys

    @Logging()
    def get_pubkey_user(self):
        """Function passes the public key"""
        return self.keys.publickey().export_key()

    @Logging()
    def create_current_encrypt(self, current_chat_key):
        """Create an encryption object."""
        self.current_encrypt = PKCS1_OAEP.new(key=RSA.import_key(current_chat_key), hashAlgo=self.HASH_FUNCTION)

    @Logging()
    def message_encryption(self, message_text):
        """Message encryption before sending."""
        try:
            message_text_encrypted = bytearray()

            while len(message_text) > self.INPUT_BLOCK_SIZE:
                block = message_text[:self.INPUT_BLOCK_SIZE]
                message_text_encrypted += self.current_encrypt.encrypt(block.encode('utf8'))
                message_text = message_text[self.INPUT_BLOCK_SIZE:]

            if len(message_text) > 0:
                block = message_text
                message_text_encrypted += self.current_encrypt.encrypt(block.encode('utf8'))

            message_text_encrypted_base64 = base64.b64encode(
                message_text_encrypted).decode('ascii')

        except (ValueError, TypeError):
            LOGGER.warning(
                self, 'Error', 'Failed to encode message.')
            return None
        return message_text_encrypted_base64

    @Logging()
    def message_decryption(self, encrypted_message):
        """Message decryption function after receiving."""
        try:
            encrypted_message_str = base64.b64decode(encrypted_message)
            decrypted_message = ''
            while len(encrypted_message_str) > self.OUTPUT_BLOCK_SIZE:
                block = encrypted_message_str[:self.OUTPUT_BLOCK_SIZE]
                decrypted = self.decrypter.decrypt(block)
                decrypted_message += decrypted.decode('utf8')
                encrypted_message_str = encrypted_message_str[self.OUTPUT_BLOCK_SIZE:]

            if len(encrypted_message_str) > 0:
                block = encrypted_message_str
                decrypted = self.decrypter.decrypt(block)
                decrypted_message += decrypted.decode('utf8')
                
        except (ValueError, TypeError):
            LOGGER.warning(
                self, 'Error', 'Failed to decode message.')
            return None
        return decrypted_message
