import json
import base64
import asyncio

def create_function(
    event,
    event_handler: callable,
    use_async: bool = False,
    as_dict: bool = False
) -> None:
    """
    This function creates a Memphis function and processes events with the passed-in event_handler function.

    Args:
        event (dict):
            A dict of events given to the Function in the format: 
            {
                messages: [
                    {
                        headers: {},
                        payload: "base64_encoded_payload" 
                    },
                    ...
                ],
                inputs: {
                    "input_name": "input_value",
                    ...
                }
            }
        event_handler (callable):
            `create_function` assumes the function signature is in the format: <event_handler>(payload, headers, inputs) -> processed_payload, processed_headers. 
            This function will modify the payload and headers and return them in the modified format. This function may also be async. 
            If using asyncio set the create_function parameter use_async to True.

            Args:
                payload (bytes): The payload of the message. It will be encoded as bytes, and the user can assume UTF-8 encoding.
                headers (dict): The headers associated with the Memphis message.
                inputs (dict): The inputs associated with the Memphis function.

            Returns:
                modified_message (bytes): The modified message must be encoded into bytes before being returned from the `event_handler`.
                modified_headers (dict): The headers will be passed in and returned as a Python dictionary.

            Raises:
                Error:
                    Raises an exception of any kind when something goes wrong with processing a message. 
                    The unprocessed message and the exception will be sent to the dead-letter station.
        use_async (bool):
            When using an async function through asyncio, set this flag to True. This will await the event_handler call instead of calling it directly.
        as_dict (bool):
            Instead of taking `payload` as a bytes object, the as_dict flag can be used to have the JSON parsed to a dictionary.

    Returns:
        handler (callable):
            The Memphis function handler which is responsible for iterating over the messages in the event and passing them to the user provided event handler.
        Returns:
            The Memphis function handler returns a JSON string which represents the successful and failed messages. This is in the format:
            {
                messages: [
                    {
                        headers: {},
                        payload: "base64_encoded_payload" 
                    },
                    ...
                ],
                failed_messages[
                    {
                        headers: {},
                        payload: "base64_encoded_payload" 
                    },
                    ...
                ]
            } 
            All failed_messages will be sent to the dead letter station, and the messages will be sent to the station.
    """
    class EncodeBase64(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, bytes):
                return str(base64.b64encode(o), encoding='utf-8')
            return json.JSONEncoder.default(self, o)

    async def handler(event):
        processed_events = {}
        processed_events["messages"] = []
        processed_events["failed_messages"] = []
        for message in event["messages"]:
            try:
                payload = base64.b64decode(bytes(message['payload'], encoding='utf-8'))
                if as_dict:
                    payload =  str(payload, 'utf-8')
                    payload = json.loads(payload)

                if use_async:
                    processed_message, processed_headers = await event_handler(payload, message['headers'], event["inputs"])
                else:
                    processed_message, processed_headers = event_handler(payload, message['headers'], event["inputs"])

                if as_dict:
                    processed_message = bytes(json.dumps(processed_message), encoding='utf-8')

                if isinstance(processed_message, bytes) and isinstance(processed_headers, dict):
                    processed_events["messages"].append({
                        "headers": processed_headers,
                        "payload": processed_message
                    })
                elif processed_message is None and processed_headers is None: # filter out empty messages
                    continue
                elif processed_message is None or processed_headers is None:
                    err_msg = f"processed_messages is of type {type(processed_message)} and processed_headers is {type(processed_headers)}. Either both of these should be None or neither"
                    raise Exception(err_msg)
                else:
                    err_msg = "The returned processed_message or processed_headers were not in the right format. processed_message must be bytes and processed_headers, dict"
                    raise Exception(err_msg)
            except Exception as e:
                processed_events["failed_messages"].append({
                    "headers": message["headers"],
                    "payload": message["payload"],
                    "error": str(e)  
                })

        try:
            return json.dumps(processed_events, cls=EncodeBase64).encode('utf-8')
        except Exception as e:
            return f"Returned message types from user function are not able to be converted into JSON: {e}"

    return asyncio.run(handler(event))
