# pylint: disable=missing-module-docstring


def check_expected_logging_call(mock_logging, func_name, error_type, error_msg):
    """Utility function to check if the expected logging call was made."""
    for logged_call in mock_logging.call_args_list:
        # Check the logging format and function name
        if (
            logged_call[0][0] == "An exception occurred in function %s: %s"
            and logged_call[0][1] == func_name
        ):
            # Extract the actual exception from the logged call
            logged_exception = logged_call[0][2]
            # Check if it's of the expected type and has the expected message
            if (
                isinstance(logged_exception, error_type)
                and str(logged_exception) == error_msg
            ):
                return True
    return False
