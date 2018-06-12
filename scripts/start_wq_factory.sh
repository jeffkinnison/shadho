#!/bin/bash

export PATH="$HOME/.shadho/bin/:$PATH"

wq="work_queue_factory $@"
$wq
