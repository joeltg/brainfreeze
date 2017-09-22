from abc import ABC, abstractmethod
from tfhe import *

GATE_PARAMS = create_gate_params()

RAM_WIDTH = 8


def encode(value):
    modulo = value % 2 ** (ARCH - 1)
    binary = bin(modulo)[2:].zfill(ARCH - 1)
    string = "1" + binary if value < 0 else "0" + binary
    return [bool(int(char)) for char in string]


def decode(bits):
    value = int("".join(map(str, map(int, bits[1:]))), 2)
    return value - 2 ** (ARCH - 1) if bits[0] else value


def create_value():
    return create_ciphertext(GATE_PARAMS)


def create_bus():
    bus = []
    for i in range(ARCH):
        bus.append(create_value())
    return bus


def create_ram():
    ram = []
    for i in range(RAM_WIDTH):
        ram.append(create_bus())
    return ram


class Circuit(ABC):
    @abstractmethod
    def eval(self, cloud_key):
        pass


class Gate(Circuit):
    def __init__(self, apply, inputs):
        Circuit.__init__(self)
        self.inputs = inputs
        self.apply = apply
        self.value = create_value()

    def eval(self, cloud_key):
        inputs = self.inputs
        self.apply(self.value, *inputs, cloud_key)


class Not(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsNOT, inputs)


class Constant(Gate):
    def __init__(self, value):
        Gate.__init__(self, tfhe.bootsCONSTANT, (int(value),))


class NAND(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsNAND, inputs)


class OR(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsOR, inputs)


class AND(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsAND, inputs)


class XOR(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsXOR, inputs)


class XNOR(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsXNOR, inputs)


class NOR(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsNOR, inputs)


class ANDNY(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsANDNY, inputs)


class ANDYN(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsANDYN, inputs)


class ORNY(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsORNY, inputs)


class ORYN(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsORYN, inputs)


class MUX(Gate):
    def __init__(self, *inputs):
        Gate.__init__(self, tfhe.bootsMUX, inputs)


# Constants

TRUE = Constant(True)
FALSE = Constant(False)


def create_constant(value):
    bits = encode(value)
    return [TRUE.value if bit else FALSE.value for bit in bits]


ZERO = create_constant(0)
POSITIVE_ONE = create_constant(1)
NEGATIVE_ONE = create_constant(-1)


# Circuits


class BitAdder(Circuit):
    def __init__(self, a, b, c):
        Circuit.__init__(self)
        self.x1 = XOR(a, b)
        self.a1 = AND(a, b)
        self.x2 = XOR(self.x1.value, c)
        self.a2 = AND(self.x1.value, c)
        self.o1 = OR(self.a1.value, self.a2.value)

        self.carry = self.o1.value
        self.value = self.x2.value

    def eval(self, cloud_key):
        self.x1.eval(cloud_key)
        self.a1.eval(cloud_key)
        self.x2.eval(cloud_key)
        self.a2.eval(cloud_key)
        self.o1.eval(cloud_key)


class BusAdder(Circuit):
    def __init__(self, a, b):
        Circuit.__init__(self)
        self.value = [None] * ARCH
        self.adder = [None] * ARCH
        carry = FALSE.value
        for i in reversed(range(ARCH)):
            adder = BitAdder(a[i], b[i], carry)
            carry = adder.carry
            self.adder[i] = adder
            self.value[i] = adder.value
        self.carry = carry

    def eval(self, cloud_key):
        for adder in reversed(self.adder):
            adder.eval(cloud_key)


class Equal(Circuit):
    def __init__(self, a, b):
        Circuit.__init__(self)
        self.gates = []
        value = TRUE.value
        for i in range(ARCH):
            equal = XNOR(a[i], b[i])
            gate = AND(value, equal.value)
            value = gate.value
            self.gates.append(equal)
            self.gates.append(gate)
        self.value = value

    def eval(self, cloud_key):
        for gate in self.gates:
            gate.eval(cloud_key)


class Zero(Circuit):
    def __init__(self, a):
        Circuit.__init__(self)
        self.gates = []
        value = TRUE.value
        for bit in a:
            gate = ANDYN(value, bit)
            value = gate.value
            self.gates.append(gate)
        self.value = value

    def eval(self, cloud_key):
        for gate in self.gates:
            gate.eval(cloud_key)


class Switch(Circuit):
    def __init__(self, condition, a, b):
        Circuit.__init__(self)
        self.condition = condition
        self.muxes = [MUX(condition, a[i], b[i]) for i in range(ARCH)]
        self.value = [mux.value for mux in self.muxes]

    def eval(self, cloud_key):
        for mux in self.muxes:
            mux.eval(cloud_key)


class Index(Circuit):
    def __init__(self, index, array):
        self.index = index
        self.array = array
        self.elements = []
        value = ZERO
        for i, element in enumerate(array):
            equal = Equal(create_constant(i), self.index)
            switch = Switch(equal.value, element, value)
            value = switch.value
            self.elements.append(equal)
            self.elements.append(switch)
        self.value = value

    def eval(self, cloud_key):
        for element in self.elements:
            element.eval(cloud_key)


class Direction(Circuit):
    def __init__(self, value, direction, nest, is_open, is_close):
        Circuit.__init__(self)

        self.nest_zero = Zero(nest)
        self.value_zero = Zero(value)

        self.right = ORYN(self.value_zero.value, is_close)
        self.left = AND(is_open, self.nest_zero.value)
        self.switch = MUX(direction, self.right.value, self.left.value)
        self.value = self.switch.value

    def eval(self, cloud_key):
        self.nest_zero.eval(cloud_key)
        self.value_zero.eval(cloud_key)
        self.right.eval(cloud_key)
        self.left.eval(cloud_key)
        self.switch.eval(cloud_key)


class Nest(Circuit):
    def __init__(self, direction, nest, loop, delta):
        Circuit.__init__(self)
        self.delta = Switch(loop, delta, ZERO)
        self.left = BusAdder(nest, self.delta.value)
        self.switch = Switch(direction, ZERO, self.left.value)
        self.value = self.switch.value

    def eval(self, cloud_key):
        self.delta.eval(cloud_key)
        self.left.eval(cloud_key)
        self.switch.eval(cloud_key)


# CPU is a circuit that maps
# (instruction, value, direction, nest)
# to
# (delta_instruction, delta_value, direction, nest)
# The Computer actually computes the deltas before feeding back


class CPU(Circuit):
    def __init__(self, instruction, value, direction, nest):
        Circuit.__init__(self)
        self.loop = AND(instruction[-2], instruction[-3])
        self.open = ANDYN(self.loop.value, instruction[-1])
        self.close = AND(self.loop.value, instruction[-1])
        self.delta = Switch(instruction[-1], NEGATIVE_ONE, POSITIVE_ONE)

        self.move = NOR(instruction[-2], instruction[-3])
        self.move_alive = AND(direction, self.move.value)
        self.move_delta = Switch(self.move_alive.value, self.delta.value, ZERO)

        self.edit = ANDYN(instruction[-2], instruction[-3])
        self.edit_alive = AND(direction, self.edit.value)
        self.edit_delta = Switch(self.edit_alive.value, self.delta.value, ZERO)

        self.direction = Direction(value, direction, nest, self.open.value, self.close.value)
        self.nest = Nest(direction, nest, self.loop.value, self.delta.value)

    def eval(self, cloud_key):
        self.loop.eval(cloud_key)
        self.open.eval(cloud_key)
        self.close.eval(cloud_key)
        self.delta.eval(cloud_key)

        self.move.eval(cloud_key)
        self.move_alive.eval(cloud_key)
        self.move_delta.eval(cloud_key)

        self.edit.eval(cloud_key)
        self.edit_alive.eval(cloud_key)
        self.edit_delta.eval(cloud_key)

        self.direction.eval(cloud_key)
        self.nest.eval(cloud_key)


class RAM(Circuit):
    def __init__(self, data, data_pointer, data_delta):
        self.data = data
        self.pointer = data_pointer
        self.delta = data_delta
        self.elements = []
        self.value = []
        for i in range(RAM_WIDTH):
            equal = Equal(self.pointer, create_constant(i))
            switch = Switch(equal.value, self.delta, ZERO)
            adder = BusAdder(self.data[i], switch.value)
            self.elements.append(equal)
            self.elements.append(switch)
            self.elements.append(adder)
            self.value.append(adder.value)

    def eval(self, cloud_key):
        for element in self.elements:
            element.eval(cloud_key)


class Computer(Circuit):
    def __init__(self, instructions):
        Circuit.__init__(self)
        self.instructions = instructions
        self.instruction_pointer = create_bus()
        self.instruction_index = Index(self.instruction_pointer, self.instructions)
        self.instruction = self.instruction_index.value
        self.direction = create_value()
        self.nest = create_bus()

        self.data = create_ram()
        self.data_pointer = create_bus()
        self.data_index = Index(self.data_pointer, self.data)
        self.value = self.data_index.value

        self.cpu = CPU(self.instruction, self.value, self.direction, self.nest)

        self.instruction_switch = Switch(self.cpu.direction.value, POSITIVE_ONE, NEGATIVE_ONE)
        self.instruction_adder = BusAdder(self.instruction_switch.value, self.instruction_pointer)

        self.data_adder = BusAdder(self.cpu.move_delta.value, self.data_pointer)

        self.ram = RAM(self.data, self.data_pointer, self.cpu.edit_delta.value)

    def eval(self, cloud_key):
        self.instruction_index.eval(cloud_key)
        self.data_index.eval(cloud_key)
        self.cpu.eval(cloud_key)
        self.instruction_switch.eval(cloud_key)
        self.instruction_adder.eval(cloud_key)
        self.data_adder.eval(cloud_key)
        self.ram.eval(cloud_key)

        copy_bus(self.instruction_pointer, self.instruction_adder.value, cloud_key)
        copy_bus(self.data_pointer, self.data_adder.value, cloud_key)
        copy_bit(self.direction, self.cpu.direction.value, cloud_key)
        copy_bus(self.nest, self.cpu.nest.value, cloud_key)
        for r, v in zip(self.data, self.ram.value):
            copy_bus(r, v, cloud_key)

    def init(self, cloud_key):
        for bit in self.instruction_pointer:
            tfhe.bootsCONSTANT(bit, 0, cloud_key)
        for bit in self.nest:
            tfhe.bootsCONSTANT(bit, 0, cloud_key)
        for bus in self.data:
            for bit in bus:
                tfhe.bootsCONSTANT(bit, 0, cloud_key)
        for bit in self.data_pointer:
            tfhe.bootsCONSTANT(bit, 0, cloud_key)
        tfhe.bootsCONSTANT(self.direction, 1, cloud_key)


'''
00000000 | 0x00 | move data pointer right
00000001 | 0x01 | move data pointer left
00000010 | 0x02 | increment data value
00000011 | 0x03 | decrement data value
00000100 | 0x04 | output data value
00000101 | 0x05 | input data value
00000110 | 0x06 | mark start of loop
00000111 | 0x07 | loop to start mark
'''

operations = {
    ">": encode(0),
    "<": encode(1),
    "+": encode(2),
    "-": encode(3),
    ".": encode(4),
    ",": encode(5),
    "[": encode(6),
    "]": encode(7)
}


def create_rom(code, secret_key):
    rom = []
    for char in code:
        bits = operations[char]
        bus = create_bus()
        for value, sample in zip(bits, bus):
            encrypt(sample, value, secret_key)
        rom.append(bus)
    return rom


def copy_bit(result, value, cloud_key):
    tfhe.bootsCOPY(result, value, cloud_key)


def copy_bus(result, value, cloud_key):
    for r, v in zip(result, value):
        copy_bit(r, v, cloud_key)


def get(bus, secret_key):
    bits = [decrypt(sample, secret_key) for sample in bus]
    return decode(bits)


dir_path = os.path.dirname(os.path.realpath(__file__))


def load_from_path(name):
    if os.path.exists(dir_path + "/" + name):
        bus = create_bus()
        for i in range(ARCH):
            file = dir_path + "/" + name + "/" + str(i)
            tfhe_io.import_ciphertext(file.encode(), bus[i], GATE_PARAMS)
        return bus


def write_to_path(name, bus):
    if not os.path.exists(dir_path + "/" + name):
        os.makedirs(dir_path + "/" + name)
    for i in range(ARCH):
        file = dir_path + "/" + name + "/" + str(i)
        tfhe_io.export_ciphertext(file.encode(), bus[i], GATE_PARAMS)
