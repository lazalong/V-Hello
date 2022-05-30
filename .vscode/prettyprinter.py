import gdb


class StringPrinter:
    def __init__(self, val):
        self.val = val

    def to_string(self):
        buffer = gdb.inferiors()[0].read_memory(self.val['str'], self.val['len'])
        return str(buffer, 'mbcs')  # depending on the default encoding this must be changed


class ArrayPrinter:
    def __init__(self, val, _type):
        self.val = val
        self.length = int(self.val['len'])
        self.mem = self.val['data']
        self._type = _type[6:]

    def to_string(self):
        return f"{self._type} array:"

    def next_element(self):
        try:
            for i in range(self.length):
                ptr = self.mem.cast(gdb.lookup_type(self._type).pointer())
                ptr += i
                yield str(i), str(ptr.dereference())
        except gdb.error:
            return

    def children(self):
        return self.next_element()

    def display_hint(self):
        return "array"


class MapPrinter:
    def __init__(self, val, _type):
        self.val = val
        self.length = int(self.val['len'])
        self.values = self.val['key_values']['values']
        self.keys = self.val['key_values']['keys']
        _, self.key_type, self.value_type = _type.split('_', 2)

    def to_string(self):
        return None  # "Map:"

    def next_element(self):
        for i in range(self.length):
            key_ptr = self.keys.cast(gdb.lookup_type(self.key_type).pointer())
            val_ptr = self.values.cast(gdb.lookup_type(self.value_type).pointer())
            key_ptr += i
            val_ptr += i
            yield str(key_ptr.dereference()), str(val_ptr.dereference())

    def children(self):
        return self.next_element()

    def display_hint(self):
        return None


class UTF16StringPrinter:
    def __init__(self, val):
        self.val = val
        self.value = ''
        i = 100
        while True:
            buffer = gdb.inferiors()[0].read_memory(self.val, 2)
            value = bytes(buffer).decode("utf-16-le")
            self.value += value
            if value == '\x00':
                break
            i -= 1
            self.val += 1
            if i == 0:
                break

    def to_string(self):
        return self.value


def v_printer(val):
    _type = str(val.type)
    if _type == 'string':
        return StringPrinter(val)
    elif _type.startswith('Array_'):
        if _type.startswith('Array_fixed'):
            return
        elif _type.endswith('*'):
            return
        else:
            return ArrayPrinter(val, _type)
    elif _type.startswith('Map_'):
        return MapPrinter(val, _type)
    # elif _type == 'u16 *':
        # return UTF16StringPrinter(val)


gdb.pretty_printers.append(v_printer)