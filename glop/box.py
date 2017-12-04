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


def unquote(obj, val):
    if isinstance(obj, list):
        if obj[0] == 'if':
            if val[obj[1]]:
                return [unquote(obj[2], val)]
            elif len(obj) == 4:
                return [unquote(obj[3], val)]
            else:
                return []
        elif obj[0] == 'for':
            r = []
            var = obj[1]
            for v in val[obj[2]]:
                r.append(unquote(obj[3], {var: v}))
            return r
        elif obj[0] == 'var':
            return val[obj[1]]
        else:
            r = []
            for el in obj:
                if isinstance(el, list) and el:
                    if el[0] in ('if', 'for'):
                        r.extend(unquote(el, val))
                    else:
                        r.append(unquote(el, val))
                else:
                    r.append(unquote(el, val))
            return r 
    else:
        return obj


def format(box):
    return _Box().format(box)


class _Box(object):
    def __init__(self, indent=4, width=80):
        self.indent = indent
        self.istr = ' ' * self.indent
        self.ivstr = '\n' + self.istr
        self.width = width

    def format(self, box):
        if isinstance(box, list):
            meth = getattr(self, 'op_' + box[0])
            return meth(box)
        else:
            return box

    def op_h(self, box):
        return ''.join(self.format(b) for b in box[1:])

    def op_iv(self, box):
        return self.istr + self.ivstr.join(self.op_v(box).splitlines())

    def op_v(self, box):
        return '\n'.join(self.format(b) for b in box[1:])
