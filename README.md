# wall-e-robot
Build the wall-e-robot with the cutting edge AI tools


## Features
- OpenAI
- Langchain
- TTS
- Vision Capture
- Google Search
- Weather
- Wolfram
- Whisper

## Prerequisites

```shell
git clone git@github.com:pjq/wall-e-robot.git 
pip install -r requirements.txt
```

## How to start
```shell
python wall-e.py --config myconfig.json
```

## Car API Service
- http://host:8092/api/swagger-ui.html

And basically, it support the following fields
```python
class CarAction:
    SUPPORTED_ACTIONS = ("stop", "left", "right", "up", "down")

    def __init__(self):
        self.action = ""
        self.duration = 0
        self.speed = 0
        self.angle = 0
```

## Reference
- https://github.com/pjq/rpi
- https://github.com/pjq/Alpha-Co-Vision

## Toubleshooting
```shell
ImportError: cannot import name 'BlipProcessor' from 'transformers' (/Users/i329817/miniconda3/lib/python3.10/site-packages/transformers/__init__.py)
```
You can install it
```shell
pip install git+https://github.com/huggingface/transformers
```


## Python environment
```shell
 conda create --name wall-e python=3.10 
 conda activate wall-e
 pip install -r requirements.txt
 conda deactivate wall-e
```
