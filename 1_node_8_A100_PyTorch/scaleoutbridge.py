# Copyright (c) 2019-2021 NVIDIA CORPORATION. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from queue import SimpleQueue
import torch
import mlperf_logger


class ScaleoutBridge(object):
    INIT_TIME = 'init_time'
    FWD_TIME = 'fwd_time'
    BWD_TIME = 'bwd_time'
    OPT_TIME = 'opt_time'
    LOAD_TIME = 'load_time'
    EVAL_TIME = 'eval_time'
    EPOCH_TIME = 'epoch_time'

    def __init__(self, qmax):
        print("Scaleout performance bridge is running ...")
        self.qmax = qmax
        self.fwdq = SimpleQueue()
        self.bwdq = SimpleQueue()
        self.optq = SimpleQueue()
        self.loadq = SimpleQueue()
        self.evalq = SimpleQueue()

    def push_nvtx(self, tag):
        torch.cuda.nvtx.range_push(tag)

    def pop_nvtx(self):
        torch.cuda.nvtx.range_pop()

    def add_tag(self, tag, dur, deviceid):
        if self.fwdq.qsize() > self.qmax:
            self.empty_qs()
            return 0
        if tag == self.FWD_TIME:
            self.fwdq.put((dur, deviceid))
        elif tag == self.BWD_TIME:
            self.bwdq.put((dur, deviceid))
        elif tag == self.OPT_TIME:
            self.optq.put((dur, deviceid))
        elif tag == self.LOAD_TIME:
            self.loadq.put((dur, deviceid))
        elif tag == self.EVAL_TIME:
            self.evalq.put((dur, deviceid))
        else:
            assert ("Tag not supported" and 0)
        return 1

    def print_tag(self, tag, dur, deviceid):
        mlperf_logger.log_event(
            key=tag,
            value={'r': deviceid,
                   't': dur},
            log_all_ranks=True,
            sync=False)

    def empty_qs(self):
        self.empty_q(self.fwdq, self.FWD_TIME)
        self.empty_q(self.bwdq, self.BWD_TIME)
        self.empty_q(self.optq, self.OPT_TIME)
        self.empty_q(self.loadq, self.LOAD_TIME)
        self.empty_q(self.evalq, self.EVAL_TIME)

    def empty_q(self, q, tag):
        while not q.empty():
            atuple = q.get()
            mlperf_logger.log_event(
                key=tag,
                value={'r': atuple[1],
                       't': atuple[0]},
                log_all_ranks=True,
                sync=False)
