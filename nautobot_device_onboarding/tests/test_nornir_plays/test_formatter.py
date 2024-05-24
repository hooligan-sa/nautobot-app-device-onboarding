"""Test for nornir plays in command_getter."""

import os
import json
import unittest
import yaml
from nornir.core.inventory import ConnectionOptions, Host, Defaults
from nautobot_device_onboarding.nornir_plays.formatter import perform_data_extraction, extract_and_post_process

MOCK_DIR = os.path.join("nautobot_device_onboarding", "tests", "mock")


class TestFormatter(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        with open(f"{MOCK_DIR}/mock_cisco_ios.yml", "r", encoding="utf-8") as parsing_info:
            self.platform_parsing_info = yaml.safe_load(parsing_info)
        with open(f"{MOCK_DIR}/cisco_ios/command_getter_result.json", "r", encoding="utf-8") as command_info:
            self.command_outputs = json.loads(command_info.read())
        self.host = Host(
            name="10.255.0.16",
            hostname="10.255.0.16",
            port=22,
            username="username",
            password="password",
            platform="cisco_ios",
            connection_options={
                "netmiko": ConnectionOptions(
                    hostname="10.255.0.16",
                    port=22,
                    username="username",
                    password="password",
                    platform="platform",
                )
            },
            defaults=Defaults(data={"sync_vlans": False, "sync_vrfs": False}),
        )

    def test_perform_data_extraction_simple_host_values(self):
        self.assertEqual("10.255.0.16", self.host.name)
        self.assertFalse(self.host.data.get("sync_vlans"))
        self.assertFalse(self.host.data.get("sync_vrfs"))

    def test_perform_data_extraction_sync_devices(self):
        actual_result = perform_data_extraction(
            self.host, self.platform_parsing_info["sync_devices"], self.command_outputs, job_debug=False
        )
        expected_parsed_result = {
            "device_type": "WS-C4948E",
            "hostname": "dummy_rtr",
            "mask_length": 16,
            "mgmt_interface": "Vlan1",
            "serial": "CAT1451S15C",
        }
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_empty_command_result_str(self):
        parsed_command_output = ""
        actual_result = extract_and_post_process(
            parsed_command_output,
            self.platform_parsing_info["sync_devices"]["serial"],
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            None,
            False,
        )
        expected_parsed_result = ("", [])
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_empty_command_result_list(self):
        parsed_command_output = []
        actual_result = extract_and_post_process(
            parsed_command_output,
            self.platform_parsing_info["sync_devices"]["serial"],
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            None,
            False,
        )
        expected_parsed_result = ([], [])
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_empty_command_result_dict(self):
        parsed_command_output = {}
        actual_result = extract_and_post_process(
            parsed_command_output,
            self.platform_parsing_info["sync_devices"]["serial"],
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            None,
            False,
        )
        expected_parsed_result = ({}, [])
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_empty_command_result_str_with_iterable(self):
        parsed_command_output = ""
        actual_result = extract_and_post_process(
            parsed_command_output,
            self.platform_parsing_info["sync_devices"]["serial"],
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            "str",
            False,
        )
        expected_parsed_result = ("", "")
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_empty_command_result_list_with_iterable(self):
        parsed_command_output = []
        actual_result = extract_and_post_process(
            parsed_command_output,
            self.platform_parsing_info["sync_devices"]["serial"],
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            "dict",
            False,
        )
        expected_parsed_result = ([], {})
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_empty_command_result_dict_with_iterable(self):
        parsed_command_output = {}
        actual_result = extract_and_post_process(
            parsed_command_output,
            self.platform_parsing_info["sync_devices"]["serial"],
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            "dict",
            False,
        )
        expected_parsed_result = ({}, {})
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_result_dict_with_iterable(self):
        parsed_command_output = self.command_outputs["show version"]
        actual_result = extract_and_post_process(
            parsed_command_output,
            self.platform_parsing_info["sync_devices"]["serial"]["commands"][0],
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            None,
            False,
        )
        expected_parsed_result = (["CAT1451S15C"], "CAT1451S15C")
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_result_json_string(self):
        parsed_command_output = '{"foo": "bar"}'
        actual_result = extract_and_post_process(
            parsed_command_output,
            {
                "command": "show version",
                "parser": "textfsm",
                "jpath": "foo",
            },
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            None,
            False,
        )
        expected_parsed_result = ("bar", "bar")
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_result_python_dict(self):
        parsed_command_output = {"foo": "bar"}
        actual_result = extract_and_post_process(
            parsed_command_output,
            {
                "command": "show version",
                "parser": "textfsm",
                "jpath": "foo",
            },
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            None,
            False,
        )
        expected_parsed_result = ("bar", "bar")
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_result_non_json_string(self):
        parsed_command_output = "jeff"
        actual_result = extract_and_post_process(
            parsed_command_output,
            {
                "command": "show version",
                "parser": "textfsm",
                "jpath": "foo",
            },
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            None,
            False,
        )
        expected_parsed_result = ([], [])
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_result_non_json_string_with_iterable(self):
        parsed_command_output = "jeff"
        actual_result = extract_and_post_process(
            parsed_command_output,
            {
                "command": "show version",
                "parser": "textfsm",
                "jpath": "foo",
            },
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            "dict",
            False,
        )
        expected_parsed_result = ([], {})
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_result_list_to_dict(self):
        parsed_command_output = [{"foo": {"bar": "moo"}}]
        actual_result = extract_and_post_process(
            parsed_command_output,
            {
                "command": "show version",
                "parser": "textfsm",
                "jpath": "[*].foo",
            },
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            "dict",
            False,
        )
        expected_parsed_result = ([{"bar": "moo"}], {"bar": "moo"})
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_result_list_to_string(self):
        parsed_command_output = ["foo"]
        actual_result = extract_and_post_process(
            parsed_command_output,
            {
                "command": "show version",
                "parser": "textfsm",
                "jpath": "[*]",
            },
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            "str",
            False,
        )
        expected_parsed_result = (["foo"], "foo")
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_result_default_iterable(self):
        parsed_command_output = [{"foo": {"bar": "moo"}}]
        actual_result = extract_and_post_process(
            parsed_command_output,
            {
                "command": "show version",
                "parser": "textfsm",
                "jpath": "[*].foo",
            },
            {"obj": "1.1.1.1", "original_host": "1.1.1.1"},
            None,
            False,
        )
        expected_parsed_result = ([{"bar": "moo"}], [{"bar": "moo"}])
        self.assertEqual(expected_parsed_result, actual_result)

    def test_extract_and_post_process_sync_network_no_vlans_no_vrfs(self):
        actual_result = perform_data_extraction(
            self.host, self.platform_parsing_info["sync_network_data"], self.command_outputs, job_debug=False
        )
        expected_parsed_result = {
            "serial": "CAT1451S15C",
            "interfaces": {
                "GigabitEthernet0/0": {
                    "ip_addresses": [{"ip_address": "", "prefix_length": ""}],
                    "mac_address": "fa16.3e57.336f",
                    "mtu": "1500",
                    "description": "",
                    "link_status": "False",
                    "802.1Q_mode": "",
                    "lag": [],
                    "type": "other",
                },
                "GigabitEthernet0/1": {
                    "802.1Q_mode": "tagged-all",
                    "description": "to iosvl2-2",
                    "ip_addresses": [{"ip_address": "", "prefix_length": ""}],
                    "lag": "Port-channel1",
                    "link_status": "True",
                    "mac_address": "fa16.3e4f.41cc",
                    "mtu": "1500",
                    "type": "other",
                },
                "GigabitEthernet0/2": {
                    "802.1Q_mode": "access",
                    "description": ["to iosvl2-4", "Port"],
                    "ip_addresses": [{"ip_address": "", "prefix_length": ""}, {"ip_address": "", "prefix_length": ""}],
                    "lag": "Port-channel1",
                    "link_status": "True",
                    "mac_address": ["fa16.3ea3.3e49", "78da.6eaf.3b82"],
                    "mtu": ["1500", "1500"],
                    "type": "other",
                },
                "GigabitEthernet0/3": {
                    "802.1Q_mode": "",
                    "description": "to iosvl2-3",
                    "ip_addresses": [{"ip_address": "", "prefix_length": ""}],
                    "lag": [],
                    "link_status": "True",
                    "mac_address": "fa16.3e31.2c47",
                    "mtu": "1500",
                    "type": "other",
                },
                "GigabitEthernet1/0": {
                    "802.1Q_mode": "",
                    "description": "to iosvl2-3",
                    "ip_addresses": [{"ip_address": "", "prefix_length": ""}],
                    "lag": "Port-channel3",
                    "link_status": "True",
                    "mac_address": "fa16.3ec8.50ab",
                    "mtu": "1500",
                    "type": "other",
                },
                "Loopback0": {
                    "802.1Q_mode": "",
                    "description": "Loopback",
                    "ip_addresses": [{"ip_address": "", "prefix_length": ""}],
                    "lag": [],
                    "link_status": "True",
                    "mac_address": "",
                    "mtu": "1514",
                    "type": "other",
                },
                "Port-channel1": {
                    "802.1Q_mode": "",
                    "description": "",
                    "ip_addresses": [{"ip_address": "", "prefix_length": ""}],
                    "lag": [],
                    "link_status": "False",
                    "mac_address": "fa16.3e4f.41cc",
                    "mtu": "1500",
                    "type": "lag",
                },
                "Port-channel3": {
                    "802.1Q_mode": "",
                    "description": "",
                    "ip_addresses": [{"ip_address": "", "prefix_length": ""}],
                    "lag": [],
                    "link_status": "False",
                    "mac_address": "fa16.3e4f.41c2",
                    "mtu": "1500",
                    "type": "lag",
                },
                "Vlan1": {
                    "802.1Q_mode": "",
                    "description": "OOB Management",
                    "ip_addresses": [{"ip_address": "10.255.0.16", "prefix_length": "16"}],
                    "lag": [],
                    "link_status": "True",
                    "mac_address": "fa16.3e57.8001",
                    "mtu": "1500",
                    "type": "virtual",
                },
            },
        }
        self.assertEqual(expected_parsed_result, actual_result)
