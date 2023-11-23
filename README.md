<a href="![Github (4)](https://github.com/memphisdev/memphis-terraform/assets/107035359/a5fe5d0f-22e1-4445-957d-5ce4464e61b1)">![Github (4)](https://github.com/memphisdev/memphis-terraform/assets/107035359/a5fe5d0f-22e1-4445-957d-5ce4464e61b1)</a>
<p align="center">
<a href="https://memphis.dev/discord"><img src="https://img.shields.io/discord/963333392844328961?color=6557ff&label=discord" alt="Discord"></a>
<a href="https://github.com/memphisdev/memphis/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/memphisdev/memphis?color=6557ff"></a> 
  <img src="https://img.shields.io/npm/dw/memphis-dev?color=ffc633&label=installations">
<a href="https://github.com/memphisdev/memphis/blob/master/CODE_OF_CONDUCT.md"><img src="https://img.shields.io/badge/Code%20of%20Conduct-v1.0-ff69b4.svg?color=ffc633" alt="Code Of Conduct"></a> 
<img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/memphisdev/memphis?color=61dfc6">
<img src="https://img.shields.io/github/last-commit/memphisdev/memphis?color=61dfc6&label=last%20commit">
</p>

<div align="center">
  
  <img width="200" alt="CNCF Silver Member" src="https://github.com/cncf/artwork/raw/master/other/cncf-member/silver/color/cncf-member-silver-color.svg#gh-light-mode-only">
  <img width="200" alt="CNCF Silver Member" src="https://github.com/cncf/artwork/raw/master/other/cncf-member/silver/white/cncf-member-silver-white.svg#gh-dark-mode-only">
 

  <h4>

**[Memphis.dev](https://memphis.dev)** is a highly scalable, painless, and effortless data streaming platform.<br>
Made to enable developers and data teams to collaborate and build<br>
real-time and streaming apps fast.

  </h4>
  
</div>

## Installation

```sh
$ pip3 install memphis-functions
```

## Importing

```python
from memphis import create_function
```

### Creating a Memphis function
Memphis provides a create_function utility for more easily creatin Memphis Functions.

The user created `event_handler` will be called for every message in the given batch of events. The user's `event_handler` will take in a `msg_payload` as bytes, `msg_headers` as a dict and `inputs` as a dict, and should return a modified version of the payload and headers in the same data types.

The user function should raise an exception if the message processing has failed. If any exception is raised (deliberately or by a failed operation) the message will be sent to the dead letter station.

If the returned modified version of the `msg_payload` or `msg_headers` are returned as `None`, then the message will be skipped and will not be sent to the station or dead letter station.

> Make sure to encode the modified `msg_payload` bytes object with utf-8 encoding!

This example function takes the bytes object `msg_payload` and encodes it into a string so that it may be parsed as JSON.  

```python
import json
import base64
from memphis import create_function

def handler(event, context): # The name of this file and this function should match the handler field in the memphis.yaml file in the following format <file name>.<function name>
    return create_function(event, event_handler = event_handler)

def event_handler(msg_payload, msg_headers, inputs):
    payload =  str(msg_payload, 'utf-8')
    as_json = json.loads(payload)
    as_json['modified'] = True

    return bytes(json.dumps(as_json), encoding='utf-8'), msg_headers
```

If the user would want to have a message that they would want to validate and send to the dead letter station if the validation fails then the user can raise an exception. In the following example, the field `check` is simply a boolean. The following function will send any messages which fail the `check` to the dead letter station.

```python
import json
import base64
from memphis import create_function

def handler(event, context): # The name of this file and this function should match the handler field in the memphis.yaml file in the following format <file name>.<function name>
    return create_function(event, event_handler = event_handler)

def event_handler(msg_payload, msg_headers, inputs):
    payload =  str(msg_payload, 'utf-8')
    as_json = json.loads(payload)
    if as_json['check'] == False:
        raise Exception("Validation Failed!")

    return bytes(json.dumps(as_json), encoding='utf-8'), msg_headers
```

If a user would rather just skip the message and not have it be sent to the station or dead letter station, the cuser could instead return `None`, `None`:

```python
import json
import base64
from memphis import create_function

def handler(event, context): # The name of this file and this function should match the handler field in the memphis.yaml file in the following format <file name>.<function name>
    return create_function(event, event_handler = event_handler)

def event_handler(msg_payload, msg_headers, inputs):
    payload =  str(msg_payload, 'utf-8')
    as_json = json.loads(payload)
    if as_json['check'] == False:
        return None, None

    return bytes(json.dumps(as_json), encoding='utf-8'), msg_headers
```

Lastly, if the user is using another data format like Protocol Buffers, the user may simply decode the `msg_payload` into that format instead of JSON. Assuming we have a .proto definition like this: 
```proto
syntax = "proto3";
package protobuf_example;

message Message{
    string data_field = 1;
}
```

We can decode this and get the data_field out like this:

```python
import json
import base64
from memphis import create_function
import message_pb2

def handler(event, context): # The name of this file and this function should match the handler field in the memphis.yaml file in the following format <file name>.<function name>
    return create_function(event, event_handler = event_handler)

def event_handler(msg_payload, msg_headers, inputs):
    message = message_pb2.Message()
    message.ParseFromString(base64.b64decode(encoded_str))

    # Arbitrarily changing the data_field
    message.data_field = "my new data"

    # SerializeToString returns bytes, which is the type we want
    return message.SerializeToString(), msg_headers
```
