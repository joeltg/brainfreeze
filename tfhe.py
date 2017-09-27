from tfhe_utils import *
import tfhe_utils


TFHE_LIBRARY = "libtfhe-spqlios-fma.dylib"
MINIMUM_LAMBDA = 100
ARCHITECTURE = 8

tfhe, tfhe_io = tfhe_utils.initialize(library=TFHE_LIBRARY, architecture=ARCHITECTURE)


def create_gate_params(minimum_lambda=MINIMUM_LAMBDA):
    return tfhe.new_default_gate_bootstrapping_parameters(minimum_lambda)


def delete_gate_params(gate_params):
    tfhe.delete_gate_bootstrapping_parameters(gate_params)


def create_secret_keyset(gate_params):
    return tfhe.new_random_gate_bootstrapping_secret_keyset(gate_params)


def delete_secret_keyset(secret_keyset):
    tfhe.delete_gate_bootstrapping_secret_keyset(secret_keyset)


def create_ciphertext(gate_params):
    return tfhe.new_gate_bootstrapping_ciphertext(gate_params)


def delete_ciphertext(ciphertext):
    return tfhe.delete_gate_bootstrapping_ciphertext(ciphertext)


def create_ciphertext_array(gate_params):
    return tfhe.new_gate_bootstrapping_ciphertext_array(ARCHITECTURE, gate_params)


def delete_ciphertext_array(ciphertext):
    return tfhe.delete_gate_bootstrapping_ciphertext_array(ARCHITECTURE, ciphertext)


def get_lwe_params(gate_params):
    return pointer(gate_params.contents.in_out_params)


def get_cloud_keyset(secret_keyset):
    return pointer(secret_keyset.contents.cloud)


def delete_cloud_keyset(cloud_keyset):
    tfhe.delete_gate_bootstrapping_cloud_keyset(cloud_keyset)


def encrypt(lwe_sample, value, secret_keyset):
    tfhe.bootsSymEncrypt(lwe_sample, int(value), secret_keyset)


def decrypt(lwe_sample, secret_keyset):
    return bool(tfhe.bootsSymDecrypt(lwe_sample, secret_keyset))


def import_gate_params(path):
    return tfhe_io.import_gate_params(path)


def export_gate_params(path, gate_params):
    tfhe_io.export_gate_params(path, gate_params)


def import_secret_keyset(path):
    return tfhe_io.import_secret_keyset(path)


def export_secret_keyset(path, secret_keyset):
    tfhe_io.export_secret_keyset(path, secret_keyset)


def import_cloud_keyset(path):
    return tfhe_io.import_cloud_keyset(path)


def export_cloud_keyset(path, cloud_keyset):
    tfhe_io.export_cloud_keyset(path, cloud_keyset)


def import_ciphertext(path, ciphertext, gate_params):
    tfhe_io.import_ciphertext(path, ciphertext, gate_params)


def export_ciphertext(path, ciphertext, gate_params):
    tfhe_io.export_ciphertext(path, ciphertext, gate_params)
