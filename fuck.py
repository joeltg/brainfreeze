from circuits import *


# ZERO.evaluate(cloud)
# ONE.evaluate(cloud)

# a = create_bus()
# encrypt_number(1, a, secret)
# ra = RippleCounter(a)
#
# b = POSITIVE_ONE_BUS
# rb = RippleCounter(b)


index = create_bus()
encrypt_unsigned_number(0, index, secret)

# increment = Input()
# increment.set(0, secret)
#
# decrement = Input()
# decrement.set(0, secret)

# negative = Switch(decrement, NEGATIVE_ONE_BUS, ZERO_BUS).result
# positive = Switch(increment, POSITIVE_ONE_BUS, negative).result

# delta = create_bus()
# encrypt_number(1, delta, secret)
delta = [Constant(int(bit)) for bit in encode_bits(1)]

data = RAM(index, delta)

# ripple = RippleCounter(delta)


def flush():
    # [p.evaluate(cloud) for p in delta]
    data.flush()
    # ZERO.evaluate(cloud)
    # ONE.evaluate(cloud)
    print(data.read())


# flush()


# a = create_bus()
# counter = RippleCounter(a)
#
#
# def inc(p):
#     encrypt_number(p, a, secret)
#     [i.evaluate(cloud) for i in a]
#     ONE.evaluate(cloud)
#     ZERO.evaluate(cloud)
#     return decrypt_number(counter.result, secret)


# b = create_bus()
#
# adder = RippleAdder(a, b)
# bus, carry = adder.outputs
#
#
# def add(p, q):
#     encrypt_number(p, a, secret)
#     encrypt_number(q, b, secret)
#     [i.evaluate(cloud) for i in a]
#     [i.evaluate(cloud) for i in b]
#     ONE.evaluate(cloud)
#     ZERO.evaluate(cloud)
#     print([i.get(secret) for i in a])
#     print([i.get(secret) for i in b])
#     print([i.get(secret) for i in bus])
#     print("----")
#     return decrypt_number(bus, secret)
