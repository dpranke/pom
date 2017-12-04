# Copyright 2017 Dirk Pranke. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 as found in the LICENSE file.
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def format(box, val):
    b = _Box(ind=4)
    return b.format(box, val)


class _Box(object):
    def __init__(self, ind):
        self.ind = ind

    def format(self, box, val):
        if isinstance(box, list):
            meth = getattr(self, 'op_' + box[0])
            return meth(box, val)
        else:
            return box

    def op_h(self, box, val):
        return ''.join(self.format(b, val) for b in box[1:])

    def op_if(self, box, val):
        if val.get(box[1]):
            return self.format(box[2], val)
        if len(box) == 4:
            return self.format(box[3], val)
        return ''

    def op_iv(self, box, val):
        return '    ' + '\n    '.join(self.op_v(box, val).splitlines())

    def op_v(self, box, val):
        return '\n'.join(self.format(b, val) for b in box[1:])

    def op_var(self, box, val):
        return val.get(box[1], '')
