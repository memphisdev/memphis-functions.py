from dataclasses import dataclass

@dataclass
class Errors:
    invalid_types = "The returned processed_message or processed_headers were not in the right format. processed_message must be bytes and processed_headers, dict"
    conversion_error = "Returned message types from user function are not able to be converted into JSON:"