\# API



> Note: Ollama's API docs are moving to https://docs.ollama.com/api



\## Endpoints



\- \[Generate a completion](#generate-a-completion)

\- \[Generate a chat completion](#generate-a-chat-completion)

\- \[Create a Model](#create-a-model)

\- \[List Local Models](#list-local-models)

\- \[Show Model Information](#show-model-information)

\- \[Copy a Model](#copy-a-model)

\- \[Delete a Model](#delete-a-model)

\- \[Pull a Model](#pull-a-model)

\- \[Push a Model](#push-a-model)

\- \[Generate Embeddings](#generate-embeddings)

\- \[List Running Models](#list-running-models)

\- \[Version](#version)

\- \[Experimental: Image Generation](#image-generation-experimental)



\## Conventions



\### Model names



Model names follow a `model:tag` format, where `model` can have an optional namespace such as `example/model`. Some examples are `orca-mini:3b-q8\_0` and `llama3:70b`. The tag is optional and, if not provided, will default to `latest`. The tag is used to identify a specific version.



\### Durations



All durations are returned in nanoseconds.



\### Streaming responses



Certain endpoints stream responses as JSON objects. Streaming can be disabled by providing `{"stream": false}` for these endpoints.



\## Generate a completion



```

POST /api/generate

```



Generate a response for a given prompt with a provided model. This is a streaming endpoint, so there will be a series of responses. The final response object will include statistics and additional data from the request.



\### Parameters



\- `model`: (required) the \[model name](#model-names)

\- `prompt`: the prompt to generate a response for

\- `suffix`: the text after the model response

\- `images`: (optional) a list of base64-encoded images (for multimodal models such as `llava`)

\- `think`: (for thinking models) should the model think before responding?



Advanced parameters (optional):



\- `format`: the format to return a response in. Format can be `json` or a JSON schema

\- `options`: additional model parameters listed in the documentation for the \[Modelfile](./modelfile.mdx#valid-parameters-and-values) such as `temperature`

\- `system`: system message to (overrides what is defined in the `Modelfile`)

\- `template`: the prompt template to use (overrides what is defined in the `Modelfile`)

\- `stream`: if `false` the response will be returned as a single response object, rather than a stream of objects

\- `raw`: if `true` no formatting will be applied to the prompt. You may choose to use the `raw` parameter if you are specifying a full templated prompt in your request to the API

\- `keep\_alive`: controls how long the model will stay loaded into memory following the request (default: `5m`)

\- `context` (deprecated): the context parameter returned from a previous request to `/generate`, this can be used to keep a short conversational memory



Experimental image generation parameters (for image generation models only):



> \[!WARNING]

> These parameters are experimental and may change in future versions.



\- `width`: width of the generated image in pixels

\- `height`: height of the generated image in pixels

\- `steps`: number of diffusion steps



\#### Structured outputs



Structured outputs are supported by providing a JSON schema in the `format` parameter. The model will generate a response that matches the schema. See the \[structured outputs](#request-structured-outputs) example below.



\#### JSON mode



Enable JSON mode by setting the `format` parameter to `json`. This will structure the response as a valid JSON object. See the JSON mode \[example](#request-json-mode) below.



> \[!IMPORTANT]

> It's important to instruct the model to use JSON in the `prompt`. Otherwise, the model may generate large amounts whitespace.



\### Examples



\#### Generate request (Streaming)



\##### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "llama3.2",

&#x20; "prompt": "Why is the sky blue?"

}'

```



\##### Response



A stream of JSON objects is returned:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-08-04T08:52:19.385406455-07:00",

&#x20; "response": "The",

&#x20; "done": false

}

```



The final response in the stream also includes additional data about the generation:



\- `total\_duration`: time spent generating the response

\- `load\_duration`: time spent in nanoseconds loading the model

\- `prompt\_eval\_count`: number of tokens in the prompt

\- `prompt\_eval\_duration`: time spent in nanoseconds evaluating the prompt

\- `eval\_count`: number of tokens in the response

\- `eval\_duration`: time in nanoseconds spent generating the response

\- `context`: an encoding of the conversation used in this response, this can be sent in the next request to keep a conversational memory

\- `response`: empty if the response was streamed, if not streamed, this will contain the full response



To calculate how fast the response is generated in tokens per second (token/s), divide `eval\_count` / `eval\_duration` \\\* `10^9`.



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-08-04T19:22:45.499127Z",

&#x20; "response": "",

&#x20; "done": true,

&#x20; "context": \[1, 2, 3],

&#x20; "total\_duration": 10706818083,

&#x20; "load\_duration": 6338219291,

&#x20; "prompt\_eval\_count": 26,

&#x20; "prompt\_eval\_duration": 130079000,

&#x20; "eval\_count": 259,

&#x20; "eval\_duration": 4232710000

}

```



\#### Request (No streaming)



\##### Request



A response can be received in one reply when streaming is off.



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "llama3.2",

&#x20; "prompt": "Why is the sky blue?",

&#x20; "stream": false

}'

```



\##### Response



If `stream` is set to `false`, the response will be a single JSON object:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-08-04T19:22:45.499127Z",

&#x20; "response": "The sky is blue because it is the color of the sky.",

&#x20; "done": true,

&#x20; "context": \[1, 2, 3],

&#x20; "total\_duration": 5043500667,

&#x20; "load\_duration": 5025959,

&#x20; "prompt\_eval\_count": 26,

&#x20; "prompt\_eval\_duration": 325953000,

&#x20; "eval\_count": 290,

&#x20; "eval\_duration": 4709213000

}

```



\#### Request (with suffix)



\##### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "codellama:code",

&#x20; "prompt": "def compute\_gcd(a, b):",

&#x20; "suffix": "    return result",

&#x20; "options": {

&#x20;   "temperature": 0

&#x20; },

&#x20; "stream": false

}'

```



\##### Response



```json5

{

&#x20; "model": "codellama:code",

&#x20; "created\_at": "2024-07-22T20:47:51.147561Z",

&#x20; "response": "\\n  if a == 0:\\n    return b\\n  else:\\n    return compute\_gcd(b % a, a)\\n\\ndef compute\_lcm(a, b):\\n  result = (a \* b) / compute\_gcd(a, b)\\n",

&#x20; "done": true,

&#x20; "done\_reason": "stop",

&#x20; "context": \[...],

&#x20; "total\_duration": 1162761250,

&#x20; "load\_duration": 6683708,

&#x20; "prompt\_eval\_count": 17,

&#x20; "prompt\_eval\_duration": 201222000,

&#x20; "eval\_count": 63,

&#x20; "eval\_duration": 953997000

}

```



\#### Request (Structured outputs)



\##### Request



```shell

curl -X POST http://localhost:11434/api/generate -H "Content-Type: application/json" -d '{

&#x20; "model": "llama3.1:8b",

&#x20; "prompt": "Ollama is 22 years old and is busy saving the world. Respond using JSON",

&#x20; "stream": false,

&#x20; "format": {

&#x20;   "type": "object",

&#x20;   "properties": {

&#x20;     "age": {

&#x20;       "type": "integer"

&#x20;     },

&#x20;     "available": {

&#x20;       "type": "boolean"

&#x20;     }

&#x20;   },

&#x20;   "required": \[

&#x20;     "age",

&#x20;     "available"

&#x20;   ]

&#x20; }

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.1:8b",

&#x20; "created\_at": "2024-12-06T00:48:09.983619Z",

&#x20; "response": "{\\n  \\"age\\": 22,\\n  \\"available\\": true\\n}",

&#x20; "done": true,

&#x20; "done\_reason": "stop",

&#x20; "context": \[1, 2, 3],

&#x20; "total\_duration": 1075509083,

&#x20; "load\_duration": 567678166,

&#x20; "prompt\_eval\_count": 28,

&#x20; "prompt\_eval\_duration": 236000000,

&#x20; "eval\_count": 16,

&#x20; "eval\_duration": 269000000

}

```



\#### Request (JSON mode)



> \[!IMPORTANT]

> When `format` is set to `json`, the output will always be a well-formed JSON object. It's important to also instruct the model to respond in JSON.



\##### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "llama3.2",

&#x20; "prompt": "What color is the sky at different times of the day? Respond using JSON",

&#x20; "format": "json",

&#x20; "stream": false

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-11-09T21:07:55.186497Z",

&#x20; "response": "{\\n\\"morning\\": {\\n\\"color\\": \\"blue\\"\\n},\\n\\"noon\\": {\\n\\"color\\": \\"blue-gray\\"\\n},\\n\\"afternoon\\": {\\n\\"color\\": \\"warm gray\\"\\n},\\n\\"evening\\": {\\n\\"color\\": \\"orange\\"\\n}\\n}\\n",

&#x20; "done": true,

&#x20; "context": \[1, 2, 3],

&#x20; "total\_duration": 4648158584,

&#x20; "load\_duration": 4071084,

&#x20; "prompt\_eval\_count": 36,

&#x20; "prompt\_eval\_duration": 439038000,

&#x20; "eval\_count": 180,

&#x20; "eval\_duration": 4196918000

}

```



The value of `response` will be a string containing JSON similar to:



```json

{

&#x20; "morning": {

&#x20;   "color": "blue"

&#x20; },

&#x20; "noon": {

&#x20;   "color": "blue-gray"

&#x20; },

&#x20; "afternoon": {

&#x20;   "color": "warm gray"

&#x20; },

&#x20; "evening": {

&#x20;   "color": "orange"

&#x20; }

}

```



\#### Request (with images)



To submit images to multimodal models such as `llava` or `bakllava`, provide a list of base64-encoded `images`:



\#### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "llava",

&#x20; "prompt":"What is in this picture?",

&#x20; "stream": false,

&#x20; "images": \["iVBORw0KGgoAAAANSUhEUgAAAG0AAABmCAYAAADBPx+VAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAA3VSURBVHgB7Z27r0zdG8fX743i1bi1ikMoFMQloXRpKFFIqI7LH4BEQ+NWIkjQuSWCRIEoULk0gsK1kCBI0IhrQVT7tz/7zZo888yz1r7MnDl7z5xvsjkzs2fP3uu71nNfa7lkAsm7d++Sffv2JbNmzUqcc8m0adOSzZs3Z+/XES4ZckAWJEGWPiCxjsQNLWmQsWjRIpMseaxcuTKpG/7HP27I8P79e7dq1ars/yL4/v27S0ejqwv+cUOGEGGpKHR37tzJCEpHV9tnT58+dXXCJDdECBE2Ojrqjh071hpNECjx4cMHVycM1Uhbv359B2F79+51586daxN/+pyRkRFXKyRDAqxEp4yMlDDzXG1NPnnyJKkThoK0VFd1ELZu3TrzXKxKfW7dMBQ6bcuWLW2v0VlHjx41z717927ba22U9APcw7Nnz1oGEPeL3m3p2mTAYYnFmMOMXybPPXv2bNIPpFZr1NHn4HMw0KRBjg9NuRw95s8PEcz/6DZELQd/09C9QGq5RsmSRybqkwHGjh07OsJSsYYm3ijPpyHzoiacg35MLdDSIS/O1yM778jOTwYUkKNHWUzUWaOsylE00MyI0fcnOwIdjvtNdW/HZwNLGg+sR1kMepSNJXmIwxBZiG8tDTpEZzKg0GItNsosY8USkxDhD0Rinuiko2gfL/RbiD2LZAjU9zKQJj8RDR0vJBR1/Phx9+PHj9Z7REF4nTZkxzX4LCXHrV271qXkBAPGfP/atWvu/PnzHe4C97F48eIsRLZ9+3a3f/9+87dwP1JxaF7/3r17ba+5l4EcaVo0lj3SBq5kGTJSQmLWMjgYNei2GPT1MuMqGTDEFHzeQSP2wi/jGnkmPJ/nhccs44jvDAxpVcxnq0F6eT8h4ni/iIWpR5lPyA6ETkNXoSukvpJAD3AsXLiwpZs49+fPn5ke4j10TqYvegSfn0OnafC+Tv9ooA/JPkgQysqQNBzagXY55nO/oa1F7qvIPWkRL12WRpMWUvpVDYmxAPehxWSe8ZEXL20sadYIozfmNch4QJPAfeJgW3rNsnzphBKNJM2KKODo1rVOMRYik5ETy3ix4qWNI81qAAirizgMIc+yhTytx0JWZuNI03qsrgWlGtwjoS9XwgUhWGyhUaRZZQNNIEwCiXD16tXcAHUs79co0vSD8rrJCIW98pzvxpAWyyo3HYwqS0+H0BjStClcZJT5coMm6D2LOF8TolGJtK9fvyZpyiC5ePFi9nc/oJU4eiEP0jVoAnHa9wyJycITMP78+eMeP37sXrx44d6+fdt6f82aNdkx1pg9e3Zb5W+RSRE+n+VjksQWifvVaTKFhn5O8my63K8Qabdv33b379/PiAP//vuvW7BggZszZ072/+TJk91YgkafPn166zXB1rQHFvouAWHq9z3SEevSUerqCn2/dDCeta2jxYbr69evk4MHDyY7d+7MjhMnTiTPnz9Pfv/+nfQT2ggpO2dMF8cghuoM7Ygj5iWCqRlGFml0QC/ftGmTmzt3rmsaKDsgBSPh0/8yPeLLBihLkOKJc0jp8H8vUzcxIA1k6QJ/c78tWEyj5P3o4u9+jywNPdJi5rAH9x0KHcl4Hg570eQp3+vHXGyrmEeigzQsQsjavXt38ujRo44LQuDDhw+TW7duRS1HGgMxhNXHgflaNTOsHyKvHK5Ijo2jbFjJBQK9YwFd6RVMzfgRBmEfP37suBBm/p49e1qjEP2mwTViNRo0VJWH1deMXcNK08uUjVUu7s/zRaL+oLNxz1bpANco4npUgX4G2eFbpDFyQoQxojBCpEGSytmOH8qrH5Q9vuzD6ofQylkCUmh8DBAr+q8JCyVNtWQIidKQE9wNtLSQnS4jDSsxNHogzFuQBw4cyM61UKVsjfr3ooBkPSqqQHesUPWVtzi9/vQi1T+rJj7WiTz4Pt/l3LxUkr5P2VYZaZ4URpsE+st/dujQoaBBYokbrz/8TJNQYLSonrPS9kUaSkPeZyj1AWSj+d+VBoy1pIWVNed8P0Ll/ee5HdGRhrHhR5GGN0r4LGZBaj8oFDJitBTJzIZgFcmU0Y8ytWMZMzJOaXUSrUs5RxKnrxmbb5YXO9VGUhtpXldhEUogFr3IzIsvlpmdosVcGVGXFWp2oU9kLFL3dEkSz6NHEY1sjSRdIuDFWEhd8KxFqsRi1uM/nz9/zpxnwlESONdg6dKlbsaMGS4EHFHtjFIDHwKOo46l4TxSuxgDzi+rE2jg+BaFruOX4HXa0Nnf1lwAPufZeF8/r6zD97WK2qFnGjBxTw5qNGPxT+5T/r7/7RawFC3j4vTp09koCxkeHjqbHJqArmH5UrFKKksnxrK7FuRIs8STfBZv+luugXZ2pR/pP9Ois4z+TiMzUUkUjD0iEi1fzX8GmXyuxUBRcaUfykV0YZnlJGKQpOiGB76x5GeWkWWJc3mOrK6S7xdND+W5N6XyaRgtWJFe13GkaZnKOsYqGdOVVVbGupsyA/l7emTLHi7vwTdirNEt0qxnzAvBFcnQF16xh/TMpUuXHDowhlA9vQVraQhkudRdzOnK+04ZSP3DUhVSP61YsaLtd/ks7ZgtPcXqPqEafHkdqa84X6aCeL7YWlv6edGFHb+ZFICPlljHhg0bKuk0CSvVznWsotRu433alNdFrqG45ejoaPCaUkWERpLXjzFL2Rpllp7PJU2a/v7Ab8N05/9t27Z16KUqoFGsxnI9EosS2niSYg9SpU6B4JgTrvVW1flt1sT+0ADIJU2maXzcUTraGCRaL1Wp9rUMk16PMom8QhruxzvZIegJjFU7LLCePfS8uaQdPny4jTTL0dbee5mYokQsXTIWNY46kuMbnt8Kmec+LGWtOVIl9cT1rCB0V8WqkjAsRwta93TbwNYoGKsUSChN44lgBNCoHLHzquYKrU6qZ8lolCIN0Rh6cP0Q3U6I6IXILYOQI513hJaSKAorFpuHXJNfVlpRtmYBk1Su1obZr5dnKAO+L10Hrj3WZW+E3qh6IszE37F6EB+68mGpvKm4eb9bFrlzrok7fvr0Kfv727dvWRmdVTJHw0qiiCUSZ6wCK+7XL/AcsgNyL74DQQ730sv78Su7+t/A36MdY0sW5o40ahslXr58aZ5HtZB8GH64m9EmMZ7FpYw4T6QnrZfgenrhFxaSiSGXtPnz57e9TkNZLvTjeqhr734CNtrK41L40sUQckmj1lGKQ0rC37x544r8eNXRpnVE3ZZY7zXo8NomiO0ZUCj2uHz58rbXoZ6gc0uA+F6ZeKS/jhRDUq8MKrTho9fEkihMmhxtBI1DxKFY9XLpVcSkfoi8JGnToZO5sU5aiDQIW716ddt7ZLYtMQlhECdBGXZZMWldY5BHm5xgAroWj4C0hbYkSc/jBmggIrXJWlZM6pSETsEPGqZOndr2uuuR5rF169a2HoHPdurUKZM4CO1WTPqaDaAd+GFGKdIQkxAn9RuEWcTRyN2KSUgiSgF5aWzPTeA/lN5rZubMmR2bE4SIC4nJoltgAV/dVefZm72AtctUCJU2CMJ327hxY9t7EHbkyJFseq+EJSY16RPo3Dkq1kkr7+q0bNmyDuLQcZBEPYmHVdOBiJyIlrRDq41YPWfXOxUysi5fvtyaj+2BpcnsUV/oSoEMOk2CQGlr4ckhBwaetBhjCwH0ZHtJROPJkyc7UjcYLDjmrH7ADTEBXFfOYmB0k9oYBOjJ8b4aOYSe7QkKcYhFlq3QYLQhSidNmtS2RATwy8YOM3EQJsUjKiaWZ+vZToUQgzhkHXudb/PW5YMHD9yZM2faPsMwoc7RciYJXbGuBqJ1UIGKKLv915jsvgtJxCZDubdXr165mzdvtr1Hz5LONA8jrUwKPqsmVesKa49S3Q4WxmRPUEYdTjgiUcfUwLx589ySJUva3oMkP6IYddq6HMS4o55xBJBUeRjzfa4Zdeg56QZ43LhxoyPo7Lf1kNt7oO8wWAbNwaYjIv5lhyS7kRf96dvm5Jah8vfvX3flyhX35cuX6HfzFHOToS1H4BenCaHvO8pr8iDuwoUL7tevX+b5ZdbBair0xkFIlFDlW4ZknEClsp/TzXyAKVOmmHWFVSbDNw1l1+4f90U6IY/q4V27dpnE9bJ+v87QEydjqx/UamVVPRG+mwkNTYN+9tjkwzEx+atCm/X9WvWtDtAb68Wy9LXa1UmvCDDIpPkyOQ5ZwSzJ4jMrvFcr0rSjOUh+GcT4LSg5ugkW1Io0/SCDQBojh0hPlaJdah+tkVYrnTZowP8iq1F1TgMBBauufyB33x1v+NWFYmT5KmppgHC+NkAgbmRkpD3yn9QIseXymoTQFGQmIOKTxiZIWpvAatenVqRVXf2nTrAWMsPnKrMZHz6bJq5jvce6QK8J1cQNgKxlJapMPdZSR64/UivS9NztpkVEdKcrs5alhhWP9NeqlfWopzhZScI6QxseegZRGeg5a8C3Re1Mfl1ScP36ddcUaMuv24iOJtz7sbUjTS4qBvKmstYJoUauiuD3k5qhyr7QdUHMeCgLa1Ear9NquemdXgmum4fvJ6w1lqsuDhNrg1qSpleJK7K3TF0Q2jSd94uSZ60kK1e3qyVpQK6PVWXp2/FC3mp6jBhKKOiY2h3gtUV64TWM6wDETRPLDfSakXmH3w8g9Jlug8ZtTt4kVF0kLUYYmCCtD/DrQ5YhMGbA9L3ucdjh0y8kOHW5gU/VEEmJTcL4Pz/f7mgoAbYkAAAAAElFTkSuQmCC"]

}'

```



\#### Response



```json

{

&#x20; "model": "llava",

&#x20; "created\_at": "2023-11-03T15:36:02.583064Z",

&#x20; "response": "A happy cartoon character, which is cute and cheerful.",

&#x20; "done": true,

&#x20; "context": \[1, 2, 3],

&#x20; "total\_duration": 2938432250,

&#x20; "load\_duration": 2559292,

&#x20; "prompt\_eval\_count": 1,

&#x20; "prompt\_eval\_duration": 2195557000,

&#x20; "eval\_count": 44,

&#x20; "eval\_duration": 736432000

}

```



\#### Request (Raw Mode)



In some cases, you may wish to bypass the templating system and provide a full prompt. In this case, you can use the `raw` parameter to disable templating. Also note that raw mode will not return a context.



\##### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "mistral",

&#x20; "prompt": "\[INST] why is the sky blue? \[/INST]",

&#x20; "raw": true,

&#x20; "stream": false

}'

```



\#### Request (Reproducible outputs)



For reproducible outputs, set `seed` to a number:



\##### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "mistral",

&#x20; "prompt": "Why is the sky blue?",

&#x20; "options": {

&#x20;   "seed": 123

&#x20; }

}'

```



\##### Response



```json

{

&#x20; "model": "mistral",

&#x20; "created\_at": "2023-11-03T15:36:02.583064Z",

&#x20; "response": " The sky appears blue because of a phenomenon called Rayleigh scattering.",

&#x20; "done": true,

&#x20; "total\_duration": 8493852375,

&#x20; "load\_duration": 6589624375,

&#x20; "prompt\_eval\_count": 14,

&#x20; "prompt\_eval\_duration": 119039000,

&#x20; "eval\_count": 110,

&#x20; "eval\_duration": 1779061000

}

```



\#### Generate request (With options)



If you want to set custom options for the model at runtime rather than in the Modelfile, you can do so with the `options` parameter. This example sets every available option, but you can set any of them individually and omit the ones you do not want to override.



\##### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "llama3.2",

&#x20; "prompt": "Why is the sky blue?",

&#x20; "stream": false,

&#x20; "options": {

&#x20;   "num\_keep": 5,

&#x20;   "seed": 42,

&#x20;   "num\_predict": 100,

&#x20;   "draft\_num\_predict": 4,

&#x20;   "top\_k": 20,

&#x20;   "top\_p": 0.9,

&#x20;   "min\_p": 0.0,

&#x20;   "typical\_p": 0.7,

&#x20;   "repeat\_last\_n": 33,

&#x20;   "temperature": 0.8,

&#x20;   "repeat\_penalty": 1.2,

&#x20;   "presence\_penalty": 1.5,

&#x20;   "frequency\_penalty": 1.0,

&#x20;   "penalize\_newline": true,

&#x20;   "stop": \["\\n", "user:"],

&#x20;   "numa": false,

&#x20;   "num\_ctx": 1024,

&#x20;   "num\_batch": 2,

&#x20;   "num\_gpu": 1,

&#x20;   "main\_gpu": 0,

&#x20;   "use\_mmap": true,

&#x20;   "num\_thread": 8

&#x20; }

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-08-04T19:22:45.499127Z",

&#x20; "response": "The sky is blue because it is the color of the sky.",

&#x20; "done": true,

&#x20; "context": \[1, 2, 3],

&#x20; "total\_duration": 4935886791,

&#x20; "load\_duration": 534986708,

&#x20; "prompt\_eval\_count": 26,

&#x20; "prompt\_eval\_duration": 107345000,

&#x20; "eval\_count": 237,

&#x20; "eval\_duration": 4289432000

}

```



\#### Load a model



If an empty prompt is provided, the model will be loaded into memory.



\##### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "llama3.2"

}'

```



\##### Response



A single JSON object is returned:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-12-18T19:52:07.071755Z",

&#x20; "response": "",

&#x20; "done": true

}

```



\#### Unload a model



If an empty prompt is provided and the `keep\_alive` parameter is set to `0`, a model will be unloaded from memory.



\##### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "llama3.2",

&#x20; "keep\_alive": 0

}'

```



\##### Response



A single JSON object is returned:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2024-09-12T03:54:03.516566Z",

&#x20; "response": "",

&#x20; "done": true,

&#x20; "done\_reason": "unload"

}

```



\## Generate a chat completion



```

POST /api/chat

```



Generate the next message in a chat with a provided model. This is a streaming endpoint, so there will be a series of responses. Streaming can be disabled using `"stream": false`. The final response object will include statistics and additional data from the request.



\### Parameters



\- `model`: (required) the \[model name](#model-names)

\- `messages`: the messages of the chat, this can be used to keep a chat memory

\- `tools`: list of tools in JSON for the model to use if supported

\- `think`: (for thinking models) should the model think before responding?



The `message` object has the following fields:



\- `role`: the role of the message, either `system`, `user`, `assistant`, or `tool`

\- `content`: the content of the message

\- `thinking`: (for thinking models) the model's thinking process

\- `images` (optional): a list of images to include in the message (for multimodal models such as `llava`)

\- `tool\_calls` (optional): a list of tools in JSON that the model wants to use

\- `tool\_name` (optional): add the name of the tool that was executed to inform the model of the result



Advanced parameters (optional):



\- `format`: the format to return a response in. Format can be `json` or a JSON schema.

\- `options`: additional model parameters listed in the documentation for the \[Modelfile](./modelfile.mdx#valid-parameters-and-values) such as `temperature`

\- `stream`: if `false` the response will be returned as a single response object, rather than a stream of objects

\- `keep\_alive`: controls how long the model will stay loaded into memory following the request (default: `5m`)



\### Tool calling



Tool calling is supported by providing a list of tools in the `tools` parameter. The model will generate a response that includes a list of tool calls. See the \[Chat request (Streaming with tools)](#chat-request-streaming-with-tools) example below.



Models can also explain the result of the tool call in the response. See the \[Chat request (With history, with tools)](#chat-request-with-history-with-tools) example below.



\[See models with tool calling capabilities](https://ollama.com/search?c=tool).



\### Structured outputs



Structured outputs are supported by providing a JSON schema in the `format` parameter. The model will generate a response that matches the schema. See the \[Chat request (Structured outputs)](#chat-request-structured-outputs) example below.



\### Examples



\#### Chat request (Streaming)



\##### Request



Send a chat message with a streaming response.



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "why is the sky blue?"

&#x20;   }

&#x20; ]

}'

```



\##### Response



A stream of JSON objects is returned:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-08-04T08:52:19.385406455-07:00",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": "The",

&#x20;   "images": null

&#x20; },

&#x20; "done": false

}

```



Final response:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-08-04T19:22:45.499127Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": ""

&#x20; },

&#x20; "done": true,

&#x20; "total\_duration": 4883583458,

&#x20; "load\_duration": 1334875,

&#x20; "prompt\_eval\_count": 26,

&#x20; "prompt\_eval\_duration": 342546000,

&#x20; "eval\_count": 282,

&#x20; "eval\_duration": 4535599000

}

```



\#### Chat request (Streaming with tools)



\##### Request



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "what is the weather in tokyo?"

&#x20;   }

&#x20; ],

&#x20; "tools": \[

&#x20;   {

&#x20;     "type": "function",

&#x20;     "function": {

&#x20;       "name": "get\_weather",

&#x20;       "description": "Get the weather in a given city",

&#x20;       "parameters": {

&#x20;         "type": "object",

&#x20;         "properties": {

&#x20;           "city": {

&#x20;             "type": "string",

&#x20;             "description": "The city to get the weather for"

&#x20;           }

&#x20;         },

&#x20;         "required": \["city"]

&#x20;       }

&#x20;     }

&#x20;   }

&#x20; ],

&#x20; "stream": true

}'

```



\##### Response



A stream of JSON objects is returned:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2025-07-07T20:22:19.184789Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": "",

&#x20;   "tool\_calls": \[

&#x20;     {

&#x20;       "function": {

&#x20;         "name": "get\_weather",

&#x20;         "arguments": {

&#x20;           "city": "Tokyo"

&#x20;         }

&#x20;       }

&#x20;     }

&#x20;   ]

&#x20; },

&#x20; "done": false

}

```



Final response:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2025-07-07T20:22:19.19314Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": ""

&#x20; },

&#x20; "done\_reason": "stop",

&#x20; "done": true,

&#x20; "total\_duration": 182242375,

&#x20; "load\_duration": 41295167,

&#x20; "prompt\_eval\_count": 169,

&#x20; "prompt\_eval\_duration": 24573166,

&#x20; "eval\_count": 15,

&#x20; "eval\_duration": 115959084

}

```



\#### Chat request (No streaming)



\##### Request



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "why is the sky blue?"

&#x20;   }

&#x20; ],

&#x20; "stream": false

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-12-12T14:13:43.416799Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": "Hello! How are you today?"

&#x20; },

&#x20; "done": true,

&#x20; "total\_duration": 5191566416,

&#x20; "load\_duration": 2154458,

&#x20; "prompt\_eval\_count": 26,

&#x20; "prompt\_eval\_duration": 383809000,

&#x20; "eval\_count": 298,

&#x20; "eval\_duration": 4799921000

}

```



\#### Chat request (No streaming, with tools)



\##### Request



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "what is the weather in tokyo?"

&#x20;   }

&#x20; ],

&#x20; "tools": \[

&#x20;   {

&#x20;     "type": "function",

&#x20;     "function": {

&#x20;       "name": "get\_weather",

&#x20;       "description": "Get the weather in a given city",

&#x20;       "parameters": {

&#x20;         "type": "object",

&#x20;         "properties": {

&#x20;           "city": {

&#x20;             "type": "string",

&#x20;             "description": "The city to get the weather for"

&#x20;           }

&#x20;         },

&#x20;         "required": \["city"]

&#x20;       }

&#x20;     }

&#x20;   }

&#x20; ],

&#x20; "stream": false

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2025-07-07T20:32:53.844124Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": "",

&#x20;   "tool\_calls": \[

&#x20;     {

&#x20;       "function": {

&#x20;         "name": "get\_weather",

&#x20;         "arguments": {

&#x20;           "city": "Tokyo"

&#x20;         }

&#x20;       }

&#x20;     }

&#x20;   ]

&#x20; },

&#x20; "done\_reason": "stop",

&#x20; "done": true,

&#x20; "total\_duration": 3244883583,

&#x20; "load\_duration": 2969184542,

&#x20; "prompt\_eval\_count": 169,

&#x20; "prompt\_eval\_duration": 141656333,

&#x20; "eval\_count": 18,

&#x20; "eval\_duration": 133293625

}

```



\#### Chat request (Structured outputs)



\##### Request



```shell

curl -X POST http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{

&#x20; "model": "llama3.1",

&#x20; "messages": \[{"role": "user", "content": "Ollama is 22 years old and busy saving the world. Return a JSON object with the age and availability."}],

&#x20; "stream": false,

&#x20; "format": {

&#x20;   "type": "object",

&#x20;   "properties": {

&#x20;     "age": {

&#x20;       "type": "integer"

&#x20;     },

&#x20;     "available": {

&#x20;       "type": "boolean"

&#x20;     }

&#x20;   },

&#x20;   "required": \[

&#x20;     "age",

&#x20;     "available"

&#x20;   ]

&#x20; },

&#x20; "options": {

&#x20;   "temperature": 0

&#x20; }

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.1",

&#x20; "created\_at": "2024-12-06T00:46:58.265747Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": "{\\"age\\": 22, \\"available\\": false}"

&#x20; },

&#x20; "done\_reason": "stop",

&#x20; "done": true,

&#x20; "total\_duration": 2254970291,

&#x20; "load\_duration": 574751416,

&#x20; "prompt\_eval\_count": 34,

&#x20; "prompt\_eval\_duration": 1502000000,

&#x20; "eval\_count": 12,

&#x20; "eval\_duration": 175000000

}

```



\#### Chat request (With History)



Send a chat message with a conversation history. You can use this same approach to start the conversation using multi-shot or chain-of-thought prompting.



\##### Request



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "why is the sky blue?"

&#x20;   },

&#x20;   {

&#x20;     "role": "assistant",

&#x20;     "content": "due to rayleigh scattering."

&#x20;   },

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "how is that different than mie scattering?"

&#x20;   }

&#x20; ]

}'

```



\##### Response



A stream of JSON objects is returned:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-08-04T08:52:19.385406455-07:00",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": "The"

&#x20; },

&#x20; "done": false

}

```



Final response:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-08-04T19:22:45.499127Z",

&#x20; "done": true,

&#x20; "total\_duration": 8113331500,

&#x20; "load\_duration": 6396458,

&#x20; "prompt\_eval\_count": 61,

&#x20; "prompt\_eval\_duration": 398801000,

&#x20; "eval\_count": 468,

&#x20; "eval\_duration": 7701267000

}

```



\#### Chat request (With history, with tools)



\##### Request



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "what is the weather in Toronto?"

&#x20;   },

&#x20;   // the message from the model appended to history

&#x20;   {

&#x20;     "role": "assistant",

&#x20;     "content": "",

&#x20;     "tool\_calls": \[

&#x20;       {

&#x20;         "function": {

&#x20;           "name": "get\_weather",

&#x20;           "arguments": {

&#x20;             "city": "Toronto"

&#x20;           }

&#x20;         }

&#x20;       }

&#x20;     ]

&#x20;   },

&#x20;   // the tool call result appended to history

&#x20;   {

&#x20;     "role": "tool",

&#x20;     "content": "11 degrees celsius",

&#x20;     "tool\_name": "get\_weather"

&#x20;   }

&#x20; ],

&#x20; "stream": false,

&#x20; "tools": \[

&#x20;   {

&#x20;     "type": "function",

&#x20;     "function": {

&#x20;       "name": "get\_weather",

&#x20;       "description": "Get the weather in a given city",

&#x20;       "parameters": {

&#x20;         "type": "object",

&#x20;         "properties": {

&#x20;           "city": {

&#x20;             "type": "string",

&#x20;             "description": "The city to get the weather for"

&#x20;           }

&#x20;         },

&#x20;         "required": \["city"]

&#x20;       }

&#x20;     }

&#x20;   }

&#x20; ]

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2025-07-07T20:43:37.688511Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": "The current temperature in Toronto is 11°C."

&#x20; },

&#x20; "done\_reason": "stop",

&#x20; "done": true,

&#x20; "total\_duration": 890771750,

&#x20; "load\_duration": 707634750,

&#x20; "prompt\_eval\_count": 94,

&#x20; "prompt\_eval\_duration": 91703208,

&#x20; "eval\_count": 11,

&#x20; "eval\_duration": 90282125

}

```



\#### Chat request (with images)



\##### Request



Send a chat message with images. The images should be provided as an array, with the individual images encoded in Base64.



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llava",

&#x20; "messages": \[

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "what is in this image?",

&#x20;     "images": \["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"]

&#x20;   }

&#x20; ]

}'

```



\##### Response



```json

{

&#x20; "model": "llava",

&#x20; "created\_at": "2023-12-13T22:42:50.203334Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": " The image features a cute, little pig with an angry facial expression. It's wearing a heart on its shirt and is waving in the air. This scene appears to be part of a drawing or sketching project.",

&#x20;   "images": null

&#x20; },

&#x20; "done": true,

&#x20; "total\_duration": 1668506709,

&#x20; "load\_duration": 1986209,

&#x20; "prompt\_eval\_count": 26,

&#x20; "prompt\_eval\_duration": 359682000,

&#x20; "eval\_count": 83,

&#x20; "eval\_duration": 1303285000

}

```



\#### Chat request (Reproducible outputs)



\##### Request



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "Hello!"

&#x20;   }

&#x20; ],

&#x20; "options": {

&#x20;   "seed": 101,

&#x20;   "temperature": 0

&#x20; }

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2023-12-12T14:13:43.416799Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": "Hello! How are you today?"

&#x20; },

&#x20; "done": true,

&#x20; "total\_duration": 5191566416,

&#x20; "load\_duration": 2154458,

&#x20; "prompt\_eval\_count": 26,

&#x20; "prompt\_eval\_duration": 383809000,

&#x20; "eval\_count": 298,

&#x20; "eval\_duration": 4799921000

}

```



\#### Chat request (with tools)



\##### Request



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[

&#x20;   {

&#x20;     "role": "user",

&#x20;     "content": "What is the weather today in Paris?"

&#x20;   }

&#x20; ],

&#x20; "stream": false,

&#x20; "tools": \[

&#x20;   {

&#x20;     "type": "function",

&#x20;     "function": {

&#x20;       "name": "get\_current\_weather",

&#x20;       "description": "Get the current weather for a location",

&#x20;       "parameters": {

&#x20;         "type": "object",

&#x20;         "properties": {

&#x20;           "location": {

&#x20;             "type": "string",

&#x20;             "description": "The location to get the weather for, e.g. San Francisco, CA"

&#x20;           },

&#x20;           "format": {

&#x20;             "type": "string",

&#x20;             "description": "The format to return the weather in, e.g. 'celsius' or 'fahrenheit'",

&#x20;             "enum": \["celsius", "fahrenheit"]

&#x20;           }

&#x20;         },

&#x20;         "required": \["location", "format"]

&#x20;       }

&#x20;     }

&#x20;   }

&#x20; ]

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2024-07-22T20:33:28.123648Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": "",

&#x20;   "tool\_calls": \[

&#x20;     {

&#x20;       "function": {

&#x20;         "name": "get\_current\_weather",

&#x20;         "arguments": {

&#x20;           "format": "celsius",

&#x20;           "location": "Paris, FR"

&#x20;         }

&#x20;       }

&#x20;     }

&#x20;   ]

&#x20; },

&#x20; "done\_reason": "stop",

&#x20; "done": true,

&#x20; "total\_duration": 885095291,

&#x20; "load\_duration": 3753500,

&#x20; "prompt\_eval\_count": 122,

&#x20; "prompt\_eval\_duration": 328493000,

&#x20; "eval\_count": 33,

&#x20; "eval\_duration": 552222000

}

```



\#### Load a model



If the messages array is empty, the model will be loaded into memory.



\##### Request



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[]

}'

```



\##### Response



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2024-09-12T21:17:29.110811Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": ""

&#x20; },

&#x20; "done\_reason": "load",

&#x20; "done": true

}

```



\#### Unload a model



If the messages array is empty and the `keep\_alive` parameter is set to `0`, a model will be unloaded from memory.



\##### Request



```shell

curl http://localhost:11434/api/chat -d '{

&#x20; "model": "llama3.2",

&#x20; "messages": \[],

&#x20; "keep\_alive": 0

}'

```



\##### Response



A single JSON object is returned:



```json

{

&#x20; "model": "llama3.2",

&#x20; "created\_at": "2024-09-12T21:33:17.547535Z",

&#x20; "message": {

&#x20;   "role": "assistant",

&#x20;   "content": ""

&#x20; },

&#x20; "done\_reason": "unload",

&#x20; "done": true

}

```



\## Create a Model



```

POST /api/create

```



Create a model from:



\- another model;

\- a safetensors directory; or

\- a GGUF file.



If you are creating a model from a safetensors directory or from a GGUF file, you must \[create a blob](#create-a-blob) for each of the files and then use the file name and SHA256 digest associated with each blob in the `files` field.



\### Parameters



\- `model`: name of the model to create

\- `from`: (optional) name of an existing model to create the new model from

\- `files`: (optional) a dictionary of file names to SHA256 digests of blobs to create the model from

\- `adapters`: (optional) a dictionary of file names to SHA256 digests of blobs for LORA adapters

\- `template`: (optional) the prompt template for the model

\- `license`: (optional) a string or list of strings containing the license or licenses for the model

\- `system`: (optional) a string containing the system prompt for the model

\- `parameters`: (optional) a dictionary of parameters for the model (see \[Modelfile](./modelfile.mdx#valid-parameters-and-values) for a list of parameters)

\- `messages`: (optional) a list of message objects used to create a conversation

\- `stream`: (optional) if `false` the response will be returned as a single response object, rather than a stream of objects

\- `quantize` (optional): quantize a non-quantized (e.g. float16) model



\#### Quantization types



| Type   | Recommended |

| ------ | :---------: |

| q4\_K\_M |     \\\*      |

| q4\_K\_S |             |

| q8\_0   |     \\\*      |



\### Examples



\#### Create a new model



Create a new model from an existing model.



\##### Request



```shell

curl http://localhost:11434/api/create -d '{

&#x20; "model": "mario",

&#x20; "from": "llama3.2",

&#x20; "system": "You are Mario from Super Mario Bros."

}'

```



\##### Response



A stream of JSON objects is returned:



```json

{"status":"reading model metadata"}

{"status":"creating system layer"}

{"status":"using already created layer sha256:22f7f8ef5f4c791c1b03d7eb414399294764d7cc82c7e94aa81a1feb80a983a2"}

{"status":"using already created layer sha256:8c17c2ebb0ea011be9981cc3922db8ca8fa61e828c5d3f44cb6ae342bf80460b"}

{"status":"using already created layer sha256:7c23fb36d80141c4ab8cdbb61ee4790102ebd2bf7aeff414453177d4f2110e5d"}

{"status":"using already created layer sha256:2e0493f67d0c8c9c68a8aeacdf6a38a2151cb3c4c1d42accf296e19810527988"}

{"status":"using already created layer sha256:2759286baa875dc22de5394b4a925701b1896a7e3f8e53275c36f75a877a82c9"}

{"status":"writing layer sha256:df30045fe90f0d750db82a058109cecd6d4de9c90a3d75b19c09e5f64580bb42"}

{"status":"writing layer sha256:f18a68eb09bf925bb1b669490407c1b1251c5db98dc4d3d81f3088498ea55690"}

{"status":"writing manifest"}

{"status":"success"}

```



\#### Quantize a model



Quantize a non-quantized model.



\##### Request



```shell

curl http://localhost:11434/api/create -d '{

&#x20; "model": "llama3.2:quantized",

&#x20; "from": "llama3.2:3b-instruct-fp16",

&#x20; "quantize": "q4\_K\_M"

}'

```



\##### Response



A stream of JSON objects is returned:



```json

{"status":"quantizing F16 model to Q4\_K\_M","digest":"0","total":6433687776,"completed":12302}

{"status":"quantizing F16 model to Q4\_K\_M","digest":"0","total":6433687776,"completed":6433687552}

{"status":"verifying conversion"}

{"status":"creating new layer sha256:fb7f4f211b89c6c4928ff4ddb73db9f9c0cfca3e000c3e40d6cf27ddc6ca72eb"}

{"status":"using existing layer sha256:966de95ca8a62200913e3f8bfbf84c8494536f1b94b49166851e76644e966396"}

{"status":"using existing layer sha256:fcc5a6bec9daf9b561a68827b67ab6088e1dba9d1fa2a50d7bbcc8384e0a265d"}

{"status":"using existing layer sha256:a70ff7e570d97baaf4e62ac6e6ad9975e04caa6d900d3742d37698494479e0cd"}

{"status":"using existing layer sha256:56bb8bd477a519ffa694fc449c2413c6f0e1d3b1c88fa7e3c9d88d3ae49d4dcb"}

{"status":"writing manifest"}

{"status":"success"}

```



\#### Create a model from GGUF



Create a model from a GGUF file. The `files` parameter should be filled out with the file name and SHA256 digest of the GGUF file you wish to use. Use \[/api/blobs/:digest](#push-a-blob) to push the GGUF file to the server before calling this API.



\##### Request



```shell

curl http://localhost:11434/api/create -d '{

&#x20; "model": "my-gguf-model",

&#x20; "files": {

&#x20;   "test.gguf": "sha256:432f310a77f4650a88d0fd59ecdd7cebed8d684bafea53cbff0473542964f0c3"

&#x20; }

}'

```



\##### Response



A stream of JSON objects is returned:



```json

{"status":"parsing GGUF"}

{"status":"using existing layer sha256:432f310a77f4650a88d0fd59ecdd7cebed8d684bafea53cbff0473542964f0c3"}

{"status":"writing manifest"}

{"status":"success"}

```



\#### Create a model from a Safetensors directory



The `files` parameter should include a dictionary of files for the safetensors model which includes the file names and SHA256 digest of each file. Use \[/api/blobs/:digest](#push-a-blob) to first push each of the files to the server before calling this API. Files will remain in the cache until the Ollama server is restarted.



\##### Request



```shell

curl http://localhost:11434/api/create -d '{

&#x20; "model": "fred",

&#x20; "files": {

&#x20;   "config.json": "sha256:dd3443e529fb2290423a0c65c2d633e67b419d273f170259e27297219828e389",

&#x20;   "generation\_config.json": "sha256:88effbb63300dbbc7390143fbbdd9d9fa50587b37e8bfd16c8c90d4970a74a36",

&#x20;   "special\_tokens\_map.json": "sha256:b7455f0e8f00539108837bfa586c4fbf424e31f8717819a6798be74bef813d05",

&#x20;   "tokenizer.json": "sha256:bbc1904d35169c542dffbe1f7589a5994ec7426d9e5b609d07bab876f32e97ab",

&#x20;   "tokenizer\_config.json": "sha256:24e8a6dc2547164b7002e3125f10b415105644fcf02bf9ad8b674c87b1eaaed6",

&#x20;   "model.safetensors": "sha256:1ff795ff6a07e6a68085d206fb84417da2f083f68391c2843cd2b8ac6df8538f"

&#x20; }

}'

```



\##### Response



A stream of JSON objects is returned:



```shell

{"status":"converting model"}

{"status":"creating new layer sha256:05ca5b813af4a53d2c2922933936e398958855c44ee534858fcfd830940618b6"}

{"status":"using autodetected template llama3-instruct"}

{"status":"using existing layer sha256:56bb8bd477a519ffa694fc449c2413c6f0e1d3b1c88fa7e3c9d88d3ae49d4dcb"}

{"status":"writing manifest"}

{"status":"success"}

```



\## Check if a Blob Exists



```shell

HEAD /api/blobs/:digest

```



Ensures that the file blob (Binary Large Object) used with create a model exists on the server. This checks your Ollama server and not ollama.com.



\### Query Parameters



\- `digest`: the SHA256 digest of the blob



\### Examples



\#### Request



```shell

curl -I http://localhost:11434/api/blobs/sha256:29fdb92e57cf0827ded04ae6461b5931d01fa595843f55d36f5b275a52087dd2

```



\#### Response



Return 200 OK if the blob exists, 404 Not Found if it does not.



\## Push a Blob



```

POST /api/blobs/:digest

```



Push a file to the Ollama server to create a "blob" (Binary Large Object).



\### Query Parameters



\- `digest`: the expected SHA256 digest of the file



\### Examples



\#### Request



```shell

curl -T model.gguf -X POST http://localhost:11434/api/blobs/sha256:29fdb92e57cf0827ded04ae6461b5931d01fa595843f55d36f5b275a52087dd2

```



\#### Response



Return 201 Created if the blob was successfully created, 400 Bad Request if the digest used is not expected.



\## List Local Models



```

GET /api/tags

```



List models that are available locally.



\### Examples



\#### Request



```shell

curl http://localhost:11434/api/tags

```



\#### Response



A single JSON object will be returned.



```json

{

&#x20; "models": \[

&#x20;   {

&#x20;     "name": "deepseek-r1:latest",

&#x20;     "model": "deepseek-r1:latest",

&#x20;     "modified\_at": "2025-05-10T08:06:48.639712648-07:00",

&#x20;     "size": 4683075271,

&#x20;     "digest": "0a8c266910232fd3291e71e5ba1e058cc5af9d411192cf88b6d30e92b6e73163",

&#x20;     "details": {

&#x20;       "parent\_model": "",

&#x20;       "format": "gguf",

&#x20;       "family": "qwen2",

&#x20;       "families": \["qwen2"],

&#x20;       "parameter\_size": "7.6B",

&#x20;       "quantization\_level": "Q4\_K\_M"

&#x20;     }

&#x20;   },

&#x20;   {

&#x20;     "name": "llama3.2:latest",

&#x20;     "model": "llama3.2:latest",

&#x20;     "modified\_at": "2025-05-04T17:37:44.706015396-07:00",

&#x20;     "size": 2019393189,

&#x20;     "digest": "a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72",

&#x20;     "details": {

&#x20;       "parent\_model": "",

&#x20;       "format": "gguf",

&#x20;       "family": "llama",

&#x20;       "families": \["llama"],

&#x20;       "parameter\_size": "3.2B",

&#x20;       "quantization\_level": "Q4\_K\_M"

&#x20;     }

&#x20;   }

&#x20; ]

}

```



\## Show Model Information



```

POST /api/show

```



Show information about a model including details, modelfile, template, parameters, license, system prompt.



\### Parameters



\- `model`: name of the model to show

\- `verbose`: (optional) if set to `true`, returns full data for verbose response fields



\### Examples



\#### Request



```shell

curl http://localhost:11434/api/show -d '{

&#x20; "model": "llava"

}'

```



\#### Response



```json5

{

&#x20; modelfile: '# Modelfile generated by "ollama show"\\n# To build a new Modelfile based on this one, replace the FROM line with:\\n# FROM llava:latest\\n\\nFROM /Users/matt/.ollama/models/blobs/sha256:200765e1283640ffbd013184bf496e261032fa75b99498a9613be4e94d63ad52\\nTEMPLATE """{{ .System }}\\nUSER: {{ .Prompt }}\\nASSISTANT: """\\nPARAMETER num\_ctx 4096\\nPARAMETER stop "\\u003c/s\\u003e"\\nPARAMETER stop "USER:"\\nPARAMETER stop "ASSISTANT:"',

&#x20; parameters: 'num\_keep                       24\\nstop                           "<|start\_header\_id|>"\\nstop                           "<|end\_header\_id|>"\\nstop                           "<|eot\_id|>"',

&#x20; template: "{{ if .System }}<|start\_header\_id|>system<|end\_header\_id|>\\n\\n{{ .System }}<|eot\_id|>{{ end }}{{ if .Prompt }}<|start\_header\_id|>user<|end\_header\_id|>\\n\\n{{ .Prompt }}<|eot\_id|>{{ end }}<|start\_header\_id|>assistant<|end\_header\_id|>\\n\\n{{ .Response }}<|eot\_id|>",

&#x20; details: {

&#x20;   parent\_model: "",

&#x20;   format: "gguf",

&#x20;   family: "llama",

&#x20;   families: \["llama"],

&#x20;   parameter\_size: "8.0B",

&#x20;   quantization\_level: "Q4\_0",

&#x20; },

&#x20; model\_info: {

&#x20;   "general.architecture": "llama",

&#x20;   "general.file\_type": 2,

&#x20;   "general.parameter\_count": 8030261248,

&#x20;   "general.quantization\_version": 2,

&#x20;   "llama.attention.head\_count": 32,

&#x20;   "llama.attention.head\_count\_kv": 8,

&#x20;   "llama.attention.layer\_norm\_rms\_epsilon": 0.00001,

&#x20;   "llama.block\_count": 32,

&#x20;   "llama.context\_length": 8192,

&#x20;   "llama.embedding\_length": 4096,

&#x20;   "llama.feed\_forward\_length": 14336,

&#x20;   "llama.rope.dimension\_count": 128,

&#x20;   "llama.rope.freq\_base": 500000,

&#x20;   "llama.vocab\_size": 128256,

&#x20;   "tokenizer.ggml.bos\_token\_id": 128000,

&#x20;   "tokenizer.ggml.eos\_token\_id": 128009,

&#x20;   "tokenizer.ggml.merges": \[], // populates if `verbose=true`

&#x20;   "tokenizer.ggml.model": "gpt2",

&#x20;   "tokenizer.ggml.pre": "llama-bpe",

&#x20;   "tokenizer.ggml.token\_type": \[], // populates if `verbose=true`

&#x20;   "tokenizer.ggml.tokens": \[], // populates if `verbose=true`

&#x20; },

&#x20; capabilities: \["completion", "vision"],

}

```



\## Copy a Model



```

POST /api/copy

```



Copy a model. Creates a model with another name from an existing model.



\### Examples



\#### Request



```shell

curl http://localhost:11434/api/copy -d '{

&#x20; "source": "llama3.2",

&#x20; "destination": "llama3-backup"

}'

```



\#### Response



Returns a 200 OK if successful, or a 404 Not Found if the source model doesn't exist.



\## Delete a Model



```

DELETE /api/delete

```



Delete a model and its data.



\### Parameters



\- `model`: model name to delete



\### Examples



\#### Request



```shell

curl -X DELETE http://localhost:11434/api/delete -d '{

&#x20; "model": "llama3:13b"

}'

```



\#### Response



Returns a 200 OK if successful, 404 Not Found if the model to be deleted doesn't exist.



\## Pull a Model



```

POST /api/pull

```



Download a model from the ollama library. Cancelled pulls are resumed from where they left off, and multiple calls will share the same download progress.



\### Parameters



\- `model`: name of the model to pull

\- `insecure`: (optional) allow insecure connections to the library. Only use this if you are pulling from your own library during development.

\- `stream`: (optional) if `false` the response will be returned as a single response object, rather than a stream of objects



\### Examples



\#### Request



```shell

curl http://localhost:11434/api/pull -d '{

&#x20; "model": "llama3.2"

}'

```



\#### Response



If `stream` is not specified, or set to `true`, a stream of JSON objects is returned:



The first object is the manifest:



```json

{

&#x20; "status": "pulling manifest"

}

```



Then there is a series of downloading responses. Until any of the download is completed, the `completed` key may not be included. The number of files to be downloaded depends on the number of layers specified in the manifest.



```json

{

&#x20; "status": "pulling digestname",

&#x20; "digest": "digestname",

&#x20; "total": 2142590208,

&#x20; "completed": 241970

}

```



After all the files are downloaded, the final responses are:



```json

{

&#x20;   "status": "verifying sha256 digest"

}

{

&#x20;   "status": "writing manifest"

}

{

&#x20;   "status": "removing any unused layers"

}

{

&#x20;   "status": "success"

}

```



if `stream` is set to false, then the response is a single JSON object:



```json

{

&#x20; "status": "success"

}

```



\## Push a Model



```

POST /api/push

```



Upload a model to a model library. Requires registering for ollama.ai and adding a public key first.



\### Parameters



\- `model`: name of the model to push in the form of `<namespace>/<model>:<tag>`

\- `insecure`: (optional) allow insecure connections to the library. Only use this if you are pushing to your library during development.

\- `stream`: (optional) if `false` the response will be returned as a single response object, rather than a stream of objects



\### Examples



\#### Request



```shell

curl http://localhost:11434/api/push -d '{

&#x20; "model": "mattw/pygmalion:latest"

}'

```



\#### Response



If `stream` is not specified, or set to `true`, a stream of JSON objects is returned:



```json

{ "status": "retrieving manifest" }

```



and then:



```json

{

&#x20; "status": "starting upload",

&#x20; "digest": "sha256:bc07c81de745696fdf5afca05e065818a8149fb0c77266fb584d9b2cba3711ab",

&#x20; "total": 1928429856

}

```



Then there is a series of uploading responses:



```json

{

&#x20; "status": "starting upload",

&#x20; "digest": "sha256:bc07c81de745696fdf5afca05e065818a8149fb0c77266fb584d9b2cba3711ab",

&#x20; "total": 1928429856

}

```



Finally, when the upload is complete:



```json

{"status":"pushing manifest"}

{"status":"success"}

```



If `stream` is set to `false`, then the response is a single JSON object:



```json

{ "status": "success" }

```



\## Generate Embeddings



```

POST /api/embed

```



Generate embeddings from a model



\### Parameters



\- `model`: name of model to generate embeddings from

\- `input`: text or list of text to generate embeddings for



Advanced parameters:



\- `truncate`: truncates the end of each input to fit within context length. Returns error if `false` and context length is exceeded. Defaults to `true`

\- `options`: additional model parameters listed in the documentation for the \[Modelfile](./modelfile.mdx#valid-parameters-and-values) such as `temperature`

\- `keep\_alive`: controls how long the model will stay loaded into memory following the request (default: `5m`)

\- `dimensions`: number of dimensions for the embedding



\### Examples



\#### Request



```shell

curl http://localhost:11434/api/embed -d '{

&#x20; "model": "all-minilm",

&#x20; "input": "Why is the sky blue?"

}'

```



\#### Response



```json

{

&#x20; "model": "all-minilm",

&#x20; "embeddings": \[

&#x20;   \[

&#x20;     0.010071029, -0.0017594862, 0.05007221, 0.04692972, 0.054916814,

&#x20;     0.008599704, 0.105441414, -0.025878139, 0.12958129, 0.031952348

&#x20;   ]

&#x20; ],

&#x20; "total\_duration": 14143917,

&#x20; "load\_duration": 1019500,

&#x20; "prompt\_eval\_count": 8

}

```



\#### Request (Multiple input)



```shell

curl http://localhost:11434/api/embed -d '{

&#x20; "model": "all-minilm",

&#x20; "input": \["Why is the sky blue?", "Why is the grass green?"]

}'

```



\#### Response



```json

{

&#x20; "model": "all-minilm",

&#x20; "embeddings": \[

&#x20;   \[

&#x20;     0.010071029, -0.0017594862, 0.05007221, 0.04692972, 0.054916814,

&#x20;     0.008599704, 0.105441414, -0.025878139, 0.12958129, 0.031952348

&#x20;   ],

&#x20;   \[

&#x20;     -0.0098027075, 0.06042469, 0.025257962, -0.006364387, 0.07272725,

&#x20;     0.017194884, 0.09032035, -0.051705178, 0.09951512, 0.09072481

&#x20;   ]

&#x20; ]

}

```



\## List Running Models



```

GET /api/ps

```



List models that are currently loaded into memory.



\#### Examples



\### Request



```shell

curl http://localhost:11434/api/ps

```



\#### Response



A single JSON object will be returned.



```json

{

&#x20; "models": \[

&#x20;   {

&#x20;     "name": "mistral:latest",

&#x20;     "model": "mistral:latest",

&#x20;     "size": 5137025024,

&#x20;     "digest": "2ae6f6dd7a3dd734790bbbf58b8909a606e0e7e97e94b7604e0aa7ae4490e6d8",

&#x20;     "details": {

&#x20;       "parent\_model": "",

&#x20;       "format": "gguf",

&#x20;       "family": "llama",

&#x20;       "families": \["llama"],

&#x20;       "parameter\_size": "7.2B",

&#x20;       "quantization\_level": "Q4\_0"

&#x20;     },

&#x20;     "expires\_at": "2024-06-04T14:38:31.83753-07:00",

&#x20;     "size\_vram": 5137025024

&#x20;   }

&#x20; ]

}

```



\## Generate Embedding



> Note: this endpoint has been superseded by `/api/embed`



```

POST /api/embeddings

```



Generate embeddings from a model



\### Parameters



\- `model`: name of model to generate embeddings from

\- `prompt`: text to generate embeddings for



Advanced parameters:



\- `options`: additional model parameters listed in the documentation for the \[Modelfile](./modelfile.mdx#valid-parameters-and-values) such as `temperature`

\- `keep\_alive`: controls how long the model will stay loaded into memory following the request (default: `5m`)



\### Examples



\#### Request



```shell

curl http://localhost:11434/api/embeddings -d '{

&#x20; "model": "all-minilm",

&#x20; "prompt": "Here is an article about llamas..."

}'

```



\#### Response



```json

{

&#x20; "embedding": \[

&#x20;   0.5670403838157654, 0.009260174818336964, 0.23178744316101074,

&#x20;   -0.2916173040866852, -0.8924556970596313, 0.8785552978515625,

&#x20;   -0.34576427936553955, 0.5742510557174683, -0.04222835972905159,

&#x20;   -0.137906014919281

&#x20; ]

}

```



\## Version



```

GET /api/version

```



Retrieve the Ollama version



\### Examples



\#### Request



```shell

curl http://localhost:11434/api/version

```



\#### Response



```json

{

&#x20; "version": "0.5.1"

}

```



\## Experimental Features



\### Image Generation (Experimental)



> \[!WARNING]

> Image generation is experimental and may change in future versions.



Image generation is now supported through the standard `/api/generate` endpoint when using image generation models. The API automatically detects when an image generation model is being used.



See the \[Generate a completion](#generate-a-completion) section for the full API documentation. The experimental image generation parameters (`width`, `height`, `steps`) are documented there.



\#### Example



\##### Request



```shell

curl http://localhost:11434/api/generate -d '{

&#x20; "model": "x/z-image-turbo",

&#x20; "prompt": "a sunset over mountains",

&#x20; "width": 1024,

&#x20; "height": 768

}'

```



\##### Response (streaming)



Progress updates during generation:



```json

{

&#x20; "model": "x/z-image-turbo",

&#x20; "created\_at": "2024-01-15T10:30:00.000000Z",

&#x20; "completed": 5,

&#x20; "total": 20,

&#x20; "done": false

}

```



\##### Final Response



```json

{

&#x20; "model": "x/z-image-turbo",

&#x20; "created\_at": "2024-01-15T10:30:15.000000Z",

&#x20; "image": "iVBORw0KGgoAAAANSUhEUg...",

&#x20; "done": true,

&#x20; "done\_reason": "stop",

&#x20; "total\_duration": 15000000000,

&#x20; "load\_duration": 2000000000

}

```

