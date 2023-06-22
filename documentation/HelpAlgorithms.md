## We need 2 different algos (either frontend or backend)

1. Multi pool path encoder: this will encode (in hex) the path of the multiple pools. A Python implementation fo this is in the **getMultiPoolPath.py**
2. An algo to find a path between two tokens we wish to swap: this receives all of the existing pool pairs and finds the best path (the one with less weigh aka fees). A Python implementation of this can be seen in **poolPathCreator.py**
