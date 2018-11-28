#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PiCaSo Addon
==================
Addon to comunicate with PiCaSo via Omnia

"""
from ..lib.Picaso.picaso import PiCaSo
from ..abstract import KaliAddOn


class KaliPicasoAddon(KaliAddOn):
    """
    """
    def __init__(self):
        KaliAddOn.__init__(self)
        self.picaso = PiCaSo()

    # --- Mandatory methods ---
    def setup(self, **kwargs):
        """
        Addon setup: connect to picaso.

        Params:
            kwargs: keyword arguments.

        Kwargs:
            ip (str): (mandatory) picaso ip address.
            port (int): (mandatory) picaso port.

        Returns:
            bool: True if picaso connection was successful, false otherwise.
        """
        self.picaso.connect(kwargs['ip'], kwargs['port'])
        return self.picaso.is_connected()

    def close(self):
        """
        Addon teardown: disconnect from picaso.

        Returns:
            bool: True if picaso disconnection was succesful.
        """
        self.picaso.close()
        return True
    # ---------------------------

    def card_reader_forwarding(self):
        """
        Send a 'FORWARD' command.
        """
        ret = self.picaso.card_reader_fw()
        self.checker.set_returned(ret)

    def card_reader_backwarding(self):
        """
        Send a 'BACKWARD' command.
        """
        ret = self.picaso.card_reader_rw()
        self.checker.set_returned(ret)

    def pinpad_key_pressing(self, key):
        """
        Send a 'KEY PRESS' command.

        Params:
            key (char): the key to press.
        """
        ret = self.picaso.key_press(key)
        self.checker.set_returned(ret)

    def soft_key_pressing(self, soft_key):
        """
        Send a 'SOFT KEY PRESS' command.

        Params:
            soft_key (char): the key to press.
        """
        ret = self.picaso.soft_key_press(soft_key)
        self.checker.set_returned(ret)
