from circuits import *

secret = create_secret_keyset(GATE_PARAMS)
cloud = get_cloud_keyset(secret)

TRUE.eval(cloud)
FALSE.eval(cloud)

code = compile_code("++[-]", secret)

computer = Computer(code)
computer.init(cloud)


def show():
    print("-------")
    print("ip", get(computer.instruction_pointer, secret))
    print("i", get(computer.instruction, secret))
    print("dp", get(computer.data_pointer, secret))
    print("d", get(computer.value, secret))
    print("direction", decrypt(computer.direction, secret))
    print("alive", decrypt(computer.alive, secret))
    print("nest", get(computer.nest, secret))
    print([get(i, secret) for i in computer.data])


