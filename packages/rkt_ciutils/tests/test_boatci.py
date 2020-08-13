#!/usr/bin/env python3

import unittest
from rkt_ciutils.boatci import ProcessRequestTask


class ProcessRequestTaskTest(unittest.TestCase):
    def test_is_force_building_when_on_tag(self):
        """Scenario: We are on a tag in GIT, so the CI should build images for such tag
        """

