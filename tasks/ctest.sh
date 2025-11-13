#!/bin/bash
docker run --rm -i -v "$(pwd):/host" xeus-haskell "ctest --test-dir /tmp --output-on-failure ."
