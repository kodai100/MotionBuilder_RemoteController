# MotionBuilder Remote Controller

This python script can operate MotionBuilder through UDP protocol.
Control types can be specified with json string.

Default waiting port is 10000. 

## Create Take

```
{
    "signal" : "ready",
    "value" : "[[[ Some Take Name]]]"
}
```


## Record / Play / Stop

```
{
    "signal" : "player",
    "value" : "record" or "play" or "stop"
}
```


# Attention

it will hang when receive record signal if there is no recordable devices.