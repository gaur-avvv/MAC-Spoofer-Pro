import unittest
from unittest import mock
from unittest.mock import patch, mock_open, call
import re
import sys
import os

# Import functions and variables from mac_gen and mac_spoof
from mac_gen import generate_random_mac, DEVICE_PREFIXES as MAC_GEN_DEVICE_PREFIXES # Alias for clarity
import mac_spoof

# Store original sys.argv
original_sys_argv = sys.argv

class TestMacGen(unittest.TestCase):

    def assertMacFormat(self, mac_address, context=""):
        """Helper assertion to check MAC address format and length."""
        self.assertIsNotNone(mac_address, f"MAC address should not be None. {context}")
        self.assertTrue(re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", mac_address),
                        f"MAC address {mac_address} is not in the correct format. {context}")
        self.assertEqual(len(mac_address), 17, f"MAC address {mac_address} does not have the correct length. {context}")

    def test_generate_random_mac_default(self):
        mac = generate_random_mac()
        self.assertMacFormat(mac, "Context: Default MAC")
        self.assertTrue(mac.startswith("02:"), f"Default MAC {mac} should start with '02:'.")

    def test_generate_random_mac_device_types(self):
        for device_type, prefix in MAC_GEN_DEVICE_PREFIXES.items(): # Use aliased import
            with self.subTest(device_type=device_type):
                mac = generate_random_mac(device_type)
                self.assertMacFormat(mac, f"Context: Device Type {device_type}")
                self.assertTrue(mac.upper().startswith(prefix.upper()),
                                f"MAC for {device_type} ({mac}) should start with prefix {prefix}.")

    def test_generate_random_mac_unknown_device(self):
        mac = generate_random_mac("unknown_device_type_blah_blah")
        self.assertMacFormat(mac, "Context: Unknown Device")
        self.assertTrue(mac.startswith("02:"), f"MAC for unknown device type ({mac}) should fall back to '02:'.")

    def test_generate_random_mac_malformed_prefix_in_dict(self):
        temp_prefixes = MAC_GEN_DEVICE_PREFIXES.copy()
        temp_prefixes["test_malformed_live"] = "XX:YY"

        with patch.dict('mac_gen.DEVICE_PREFIXES', temp_prefixes):
            mac = generate_random_mac("test_malformed_live")
            self.assertMacFormat(mac, "Context: Malformed Prefix from mac_gen.DEVICE_PREFIXES")
            self.assertTrue(mac.startswith("02:"),
                            f"MAC for malformed prefix device type ({mac}) should fall back to '02:'.")


class TestMacSpoof(unittest.TestCase):
    DUMMY_INTERFACE = "testeth0"
    DUMMY_ORIGINAL_MAC = "00:11:22:33:44:55"
    DUMMY_NEW_MAC = "AA:BB:CC:DD:EE:FF"
    DEVICE_PREFIXES_FROM_MAC_GEN = mac_spoof.DEVICE_PREFIXES

    original_os_path_exists = os.path.exists

    def setUp(self):
        sys.argv = [original_sys_argv[0]]
        self.expected_mac_file = mac_spoof.get_original_mac_filepath(self.DUMMY_INTERFACE)
        if os.path.exists(self.expected_mac_file):
            os.remove(self.expected_mac_file)

    def tearDown(self):
        sys.argv = original_sys_argv
        if os.path.exists(self.expected_mac_file):
            os.remove(self.expected_mac_file)

    @patch('mac_spoof.sys.exit')
    @patch('mac_spoof.argparse.ArgumentParser._print_message')
    def test_argparse_mutual_exclusivity(self, mock_print_message, mock_sys_exit):
        test_cases = [
            ['--new_mac', self.DUMMY_NEW_MAC, '--restore'],
            ['--new_mac', self.DUMMY_NEW_MAC, '--device_type', 'phone'],
            ['--device_type', 'phone', '--restore'],
            ['--new_mac', self.DUMMY_NEW_MAC, '--check']
        ]
        for args_combo in test_cases:
            with self.subTest(args=args_combo):
                sys.argv = [original_sys_argv[0], self.DUMMY_INTERFACE] + args_combo
                mac_spoof.main()
                mock_sys_exit.assert_called_with(2)
                self.assertTrue(any("not allowed with argument" in call_args[0][0] for call_args in mock_print_message.call_args_list if call_args[0]))
                mock_sys_exit.reset_mock()
                mock_print_message.reset_mock()

    @patch('mac_spoof.get_current_mac', return_value=DUMMY_ORIGINAL_MAC)
    @patch('mac_spoof.save_original_mac', return_value=True)
    @patch('mac_spoof.change_mac', return_value=True)
    @patch('mac_spoof.verify_mac_change', return_value=True)
    def test_spoof_with_new_mac(self, mock_verify, mock_change, mock_save, mock_get_current):
        sys.argv.extend([self.DUMMY_INTERFACE, '--new_mac', self.DUMMY_NEW_MAC])
        mac_spoof.main()
        mock_get_current.assert_called_once_with(self.DUMMY_INTERFACE)
        mock_save.assert_called_once_with(self.DUMMY_INTERFACE, self.DUMMY_ORIGINAL_MAC)
        mock_change.assert_called_once_with(self.DUMMY_INTERFACE, self.DUMMY_NEW_MAC)
        mock_verify.assert_called_once_with(self.DUMMY_INTERFACE, self.DUMMY_NEW_MAC)

    @patch('mac_spoof.get_current_mac', return_value=DUMMY_ORIGINAL_MAC)
    @patch('mac_spoof.generate_random_mac') # Corrected: Patch where it's used in mac_spoof module
    @patch('mac_spoof.save_original_mac', return_value=True)
    @patch('mac_spoof.change_mac', return_value=True)
    @patch('mac_spoof.verify_mac_change', return_value=True)
    def test_spoof_with_device_type(self, mock_verify, mock_change, mock_save, mock_generate_mac_in_spoof, mock_get_current):
        DEVICE_TYPE = "phone"
        phone_prefix = self.DEVICE_PREFIXES_FROM_MAC_GEN[DEVICE_TYPE].split(':')[0]
        GENERATED_DEVICE_MAC = f"{phone_prefix}:AA:BB:CC:DD:EE"
        mock_generate_mac_in_spoof.return_value = GENERATED_DEVICE_MAC # Mock the generate_random_mac imported by mac_spoof

        sys.argv.extend([self.DUMMY_INTERFACE, '--device_type', DEVICE_TYPE])
        mac_spoof.main()

        mock_get_current.assert_called_once_with(self.DUMMY_INTERFACE)
        mock_generate_mac_in_spoof.assert_called_once_with(DEVICE_TYPE) # Check the mock in mac_spoof's namespace
        mock_save.assert_called_once_with(self.DUMMY_INTERFACE, self.DUMMY_ORIGINAL_MAC)
        mock_change.assert_called_once_with(self.DUMMY_INTERFACE, GENERATED_DEVICE_MAC)
        mock_verify.assert_called_once_with(self.DUMMY_INTERFACE, GENERATED_DEVICE_MAC)

    def mock_os_path_exists_side_effect(self, path):
        if path == self.expected_mac_file:
            return self.mac_file_should_exist
        return TestMacSpoof.original_os_path_exists(path)

    @patch('mac_spoof.read_original_mac', return_value=DUMMY_ORIGINAL_MAC)
    @patch('mac_spoof.change_mac', return_value=True)
    @patch('mac_spoof.verify_mac_change', return_value=True)
    @patch('mac_spoof.os.remove')
    @patch('mac_spoof.os.path.exists')
    def test_restore_mac_success(self, mock_os_path_exists_custom, mock_os_remove, mock_verify, mock_change, mock_read_mac):
        sys.argv.extend([self.DUMMY_INTERFACE, '--restore'])
        self.mac_file_should_exist = True
        mock_os_path_exists_custom.side_effect = self.mock_os_path_exists_side_effect

        mac_spoof.main()

        mock_read_mac.assert_called_once_with(self.DUMMY_INTERFACE)
        mock_change.assert_called_once_with(self.DUMMY_INTERFACE, self.DUMMY_ORIGINAL_MAC)
        mock_verify.assert_called_once_with(self.DUMMY_INTERFACE, self.DUMMY_ORIGINAL_MAC)
        mock_os_path_exists_custom.assert_any_call(self.expected_mac_file)
        mock_os_remove.assert_called_once_with(self.expected_mac_file)

    @patch('mac_spoof.read_original_mac', return_value=None)
    @patch('mac_spoof.change_mac')
    @patch('builtins.print')
    def test_restore_mac_no_file(self, mock_print, mock_change_mac, mock_read_mac):
        sys.argv.extend([self.DUMMY_INTERFACE, '--restore'])
        mac_spoof.main()
        mock_read_mac.assert_called_once_with(self.DUMMY_INTERFACE)
        mock_change_mac.assert_not_called()
        self.assertTrue(any(f"No original MAC address found saved for {self.DUMMY_INTERFACE}" in args[0] for args, kwargs in mock_print.call_args_list if args))

    @patch('mac_spoof.get_current_mac', return_value=DUMMY_ORIGINAL_MAC)
    @patch('builtins.print')
    def test_check_mac(self, mock_print, mock_get_current):
        sys.argv.extend([self.DUMMY_INTERFACE, '--check'])
        mac_spoof.main()
        mock_get_current.assert_called_once_with(self.DUMMY_INTERFACE)
        self.assertTrue(any(self.DUMMY_ORIGINAL_MAC in args[0] for args, kwargs in mock_print.call_args_list if args))

    def test_save_and_read_original_mac_file_operations(self):
        if os.path.exists(self.expected_mac_file):
            os.remove(self.expected_mac_file)
        self.assertTrue(mac_spoof.save_original_mac(self.DUMMY_INTERFACE, self.DUMMY_ORIGINAL_MAC))
        self.assertTrue(os.path.exists(self.expected_mac_file))
        self.assertEqual(mac_spoof.read_original_mac(self.DUMMY_INTERFACE), self.DUMMY_ORIGINAL_MAC)
        os.remove(self.expected_mac_file)

    @patch('mac_spoof.subprocess.check_output', side_effect=FileNotFoundError("ifconfig not found"))
    @patch('builtins.print')
    def test_get_current_mac_ifconfig_not_found(self, mock_print, mock_check_output):
        result = mac_spoof.get_current_mac(self.DUMMY_INTERFACE)
        self.assertIsNone(result)
        self.assertTrue(any("'ifconfig' command not found" in args[0] for args,kwargs in mock_print.call_args_list if args))

    @patch('mac_spoof.subprocess.check_call', side_effect=FileNotFoundError("sudo not found"))
    @patch('builtins.print')
    def test_change_mac_sudo_not_found(self, mock_print, mock_check_call):
        result = mac_spoof.change_mac(self.DUMMY_INTERFACE, self.DUMMY_NEW_MAC)
        self.assertFalse(result)
        self.assertTrue(any("'sudo' or 'ifconfig' command not found" in args[0] for args,kwargs in mock_print.call_args_list if args))

if __name__ == '__main__':
    unittest.main(argv=sys.argv[:1])
