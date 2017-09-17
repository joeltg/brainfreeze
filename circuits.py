import os
from tfhe import *

GATE_PARAMS = create_gate_params()
BUS_WIDTH = 4

secret = create_secret_keyset(GATE_PARAMS)
cloud = get_cloud_keyset(secret)


class Gate:
    def __init__(self, apply, inputs=None, init=True):
        self.inputs = [] if inputs is None else inputs
        self.progress = [False] * len(self.inputs)

        self.children = []
        self.apply = apply
        self.result = create_ciphertext(GATE_PARAMS)
        self.values = None

        if init:
            self.initialize()

    def initialize(self):
        self.values = tuple(map(lambda g: g.result, self.inputs))
        for index, gate in enumerate(self.inputs):
            gate.attach(self, index)

    def evaluate(self, cloud):
        # print("eval", self)
        self.apply(self.result, *self.values, cloud)
        for i in range(len(self.progress)):
            self.progress[i] = False
        for gate, index in self.children:
            gate.notify(index, cloud)

    def get(self, secret):
        return decrypt(self.result, secret)

    def set(self, value, secret):
        encrypt(self.result, value, secret)

    def attach(self, gate, index):
        self.children.append((gate, index))

    def notify(self, index, cloud):
        self.progress[index] = True
        if all(self.progress):
            self.evaluate(cloud)


def void(*args):
    pass


class Input(Gate):
    def __init__(self):
        Gate.__init__(self, void)


class Constant(Gate):
    def __init__(self, value):
        Gate.__init__(self, lambda result, keyset: tfhe.bootsCONSTANT(result, value, keyset))


ZERO = Constant(0)
ONE = Constant(1)


class Not(Gate):
    def __init__(self, a):
        Gate.__init__(self, tfhe.bootsNOT, [a])


class And(Gate):
    def __init__(self, a, b, init=True):
        Gate.__init__(self, tfhe.bootsAND, [a, b], init)


class Or(Gate):
    def __init__(self, a, b):
        Gate.__init__(self, tfhe.bootsOR, [a, b])


class Xor(Gate):
    def __init__(self, a, b, init=True):
        Gate.__init__(self, tfhe.bootsXOR, [a, b], init)


class Xnor(Gate):
    def __init__(self, a, b):
        Gate.__init__(self, tfhe.bootsXNOR, [a, b])


class Mux(Gate):
    def __init__(self, a, b, c, init=True):
        Gate.__init__(self, tfhe.bootsMUX, [a, b, c], init)


class HalfAdder:
    def __init__(self, a, b, init=True):
        self.a = a
        self.b = b

        self.sum = Xor(self.a, self.b, init)
        self.carry = And(self.a, self.b, init)
        self.outputs = (self.sum, self.carry)

    def initialize(self):
        self.sum.initialize()
        self.carry.initialize()


class FullAdder:
    def __init__(self, a, b, c, init=True):
        self.half_a = HalfAdder(a, b, init)
        sum_a, carry_a = self.half_a.outputs
        self.half_b = HalfAdder(sum_a, c, init)
        sum_b, carry_b = self.half_b.outputs
        self.outputs = (sum_b, Or(carry_a, carry_b))

    def initialize(self):
        self.half_a.initialize()
        self.half_b.initialize()


class RippleAdder:
    def __init__(self, bus_a, bus_b):
        bus_c = []
        carry = ZERO
        for index in reversed(range(BUS_WIDTH)):
            a = bus_a[index]
            b = bus_b[index]
            adder = FullAdder(a, b, carry)
            v, c = adder.outputs
            carry = c
            bus_c.append(v)
        self.result = list(reversed(bus_c))
        self.outputs = (self.result, carry)


class Switch:
    def __init__(self, a, b_bus, c_bus):
        self.result = [Mux(a, b_bus[i], c_bus[i]) for i in range(BUS_WIDTH)]


class BitRegister:
    def __init__(self, live, data):
        self.result = Mux(live, data, None, False)
        self.result.inputs[2] = self.result
        self.result.progress[2] = True
        self.result.initialize()


class BitCounter:
    def __init__(self, delta, carry):
        self.delta = delta
        self.carry = carry

        self.half_a = HalfAdder(None, delta, False)
        sum_a, carry_a = self.half_a.outputs
        self.half_b = HalfAdder(sum_a, carry, False)
        sum_b, carry_b = self.half_b.outputs
        self.outputs = (sum_b, Or(carry_a, carry_b))

        self.count = sum_b
        self.half_a.sum.progress[0] = True
        self.half_a.carry.progress[0] = True
        self.half_a.sum.inputs[0] = sum_b
        self.half_a.carry.inputs[0] = sum_b

        self.half_a.initialize()
        self.half_b.initialize()


class RippleCounter:
    def __init__(self, delta_bus):
        self.delta_bus = delta_bus
        bus = []
        self.carry = ZERO
        for index in reversed(range(BUS_WIDTH)):
            counter = BitCounter(self.delta_bus[index], self.carry)
            bit, c = counter.outputs
            bus.append(bit)
            self.carry = c
        self.result = list(reversed(bus))

    def read(self):
        return decrypt_number(self.result, secret)

    def flush(self):
        for bit in self.delta_bus:
            bit.evaluate(cloud)


class Register:
    def __init__(self, live, data_bus):
        self.result = [BitRegister(live, data) for data in data_bus]
        self.outputs = self.result,


class RAM:
    def __init__(self, index_bus, delta_bus):
        self.index_bus = index_bus
        self.delta_bus = delta_bus
        self.range = [[Constant(int(j)) for j in bin(i)[2:].zfill(BUS_WIDTH)] for i in range(2 ** BUS_WIDTH)]

        # negative = Switch(decrement, NEGATIVE_ONE_BUS, ZERO_BUS).result
        # delta = Switch(increment, POSITIVE_ONE_BUS, negative).result

        self.one = Constant(1)
        self.zero_bus = [Constant(0) for i in range(BUS_WIDTH)]
        self.counters = []
        for i in range(2 ** BUS_WIDTH):
            # Assemble a circuit to test for equality to i
            equal = self.one
            for j, bit in enumerate(self.range[i]):
                equal = And(equal, Xnor(bit, self.index_bus[j]))
            delta_switch = Switch(equal, self.delta_bus, self.zero_bus)
            counter = RippleCounter(delta_switch.result)
            self.counters.append(counter)

    def read(self):
        return [decrypt_number(counter.result, secret) for counter in self.counters]

    def flush(self):
        # [p.evaluate(cloud) for p in self.zero]

        [[p.evaluate(cloud) for p in i] for i in self.range]

        self.one.evaluate(cloud)
        [p.evaluate(cloud) for p in self.zero_bus]
        [p.evaluate(cloud) for p in self.delta_bus]
        [p.evaluate(cloud) for p in self.index_bus]

        ZERO.evaluate(cloud)
        ONE.evaluate(cloud)


class ROM:
    def __init__(self, index_bus, data):
        self.index_bus = index_bus
        self.data = data
        self.range = [[Constant(int(j)) for j in bin(i)[2:].zfill(BUS_WIDTH)] for i in range(2 ** BUS_WIDTH)]
        self.one = Constant(1)
        self.minus_one_bus = [Constant(int(i)) for i in encode_bits(-1)]
        self.one_bus = [Constant(int(i)) for i in encode_bits(1)]
        self.zero_bus = [Constant(int(i)) for i in encode_bits(0)]
        for i in range(2 ** BUS_WIDTH):
            data_bus = data[i]
            equal = self.one
            for j, bit in enumerate(self.range[i]):
                equal = And(equal, Xnor(bit, self.index_bus[j]))
            operation = Switch(equal, data_bus, self.zero_bus).result
            data_pointer_delta = Switch(operation[-1], self.minus_one_bus, self.one_bus).result
            data_pointer_move = Switch(operation[-2], data_pointer_delta, self.zero_bus).result


def create_bus():
    return [Input() for i in range(BUS_WIDTH)]


def encode_bits(value):
    modulo = value % 2 ** (BUS_WIDTH - 1)
    binary = bin(modulo)[2:].zfill(BUS_WIDTH - 1)
    return "1" + binary if value < 0 else "0" + binary


def decode_bits(bits):
    value = int(bits[1:], 2)
    return value - 2 ** (BUS_WIDTH - 1) if bits[0] == "1" else value


def encrypt_unsigned_number(value, bus, secret):
    bits = bin(value)[2:].zfill(BUS_WIDTH)
    for bit, gate in zip(bits, bus):
        gate.set(int(bit), secret)


def decrypt_unsigned_number(bus, secret):
    bits = [str(gate.get(secret)) for gate in bus]
    return int("".join(bits), 2)


def encrypt_number(value, bus, secret):
    bits = encode_bits(value)
    for bit, gate in zip(bits, bus):
        gate.set(int(bit), secret)


def decrypt_number(bus, secret):
    bits = [str(gate.get(secret)) for gate in bus]
    return decode_bits("".join(bits))


def create_constant_unsigned_bus(value):
    bits = bin(value)[2:].zfill(BUS_WIDTH)
    return [ZERO if bit == "0" else ONE for bit in bits]


def create_constant_signed_bus(value):
    bits = encode_bits(value)
    return [ZERO if bit == "0" else ONE for bit in bits]

ZERO_BUS = create_constant_signed_bus(0)
POSITIVE_ONE_BUS = create_constant_signed_bus(1)
NEGATIVE_ONE_BUS = create_constant_signed_bus(-1)


dir_path = os.path.dirname(os.path.realpath(__file__))


def load_from_path(name):
    if os.path.exists(dir_path + "/" + name):
        bus = create_bus()
        for i in range(BUS_WIDTH):
            file = dir_path + "/" + name + "/" + str(i)
            tfhe_io.import_ciphertext(file.encode(), bus[i].result, GATE_PARAMS)
        return bus


def write_to_path(name, bus):
    if not os.path.exists(dir_path + "/" + name):
        os.makedirs(dir_path + "/" + name)
    for i in range(BUS_WIDTH):
        file = dir_path + "/" + name + "/" + str(i)
        tfhe_io.export_ciphertext(file.encode(), bus[i].result, GATE_PARAMS)
