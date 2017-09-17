import os
from ctypes import *

WIDTH = 64

dir_path = os.path.dirname(os.path.realpath(__file__))

'''
libtfhe-nayuki-avx.dylib
libtfhe-nayuki-portable.dylib
libtfhe-spqlios-avx.dylib
libtfhe-spqlios-fma.dylib
'''

tfhe = cdll.LoadLibrary("libtfhe-spqlios-fma.dylib")
tfhe_io = cdll.LoadLibrary(dir_path + "/tfhe_io.so")

Torus32 = c_int32


class LweParams(Structure):
    _fields_ = [("n", c_int),
                ("alpha_min", c_double),
                ("alpha_max", c_double)]


class TLweParams(Structure):
    _fields_ = [("N", c_int),
                ("k", c_int),
                ("alpha_min", c_double),
                ("alpha_max", c_double),
                ("extracted_lweparams", LweParams)]


class TGswParams(Structure):
    _fields_ = [("l", c_int),
                ("Bgbit", c_int),
                ("Bg", c_int),
                ("halfBg", c_int32),
                ("maskMod", c_uint32),
                ("tlwe_params", POINTER(TLweParams)),
                ("kpl", c_int),
                ("h", POINTER(Torus32)),
                ("offset", c_uint32)]


class LweKey(Structure):
    _fields_ = [("params", POINTER(LweParams)),
                ("key", POINTER(c_int))]


class IntPolynomial(Structure):
    _fields_ = [("N", c_int),
                ("coefs", POINTER(c_int))]


class TLweKey(Structure):
    _fields_ = [("params", POINTER(TLweParams)),
                ("key", POINTER(IntPolynomial))]


class TGswKey(Structure):
    _fields_ = [("params", POINTER(TGswParams)),
                ("tlwe_params", POINTER(TLweParams)),
                ("key", POINTER(IntPolynomial)),
                ("tlwe_key", TLweKey)]


class TFheGateBootstrappingParameterSet(Structure):
    _fields_ = [("ks_t", c_int),
                ("ks_basebit", c_int),
                ("in_out_params", POINTER(LweParams)),
                ("tgsw_params", POINTER(TGswParams))]


class TorusPolynomial(Structure):
    _fields_ = [("N", c_int),
                ("coefsT", POINTER(Torus32))]


class TLweSample(Structure):
    _fields_ = [("a", POINTER(TorusPolynomial)),
                ("b", POINTER(TorusPolynomial)),
                ("current_variance", c_double),
                ("k", c_int)]


class TGswSample(Structure):
    _fields_ = [("all_sample", POINTER(TLweSample)),
                ("bloc_sample", POINTER(POINTER(TLweSample))),
                ("k", c_int),
                ("l", c_int)]


class LweSample(Structure):
    _fields_ = [("a", POINTER(Torus32)),
                ("b", Torus32),
                ("current_variance", c_double)]


class LweKeySwitchKey(Structure):
    _fields_ = [("n", c_int),
                ("t", c_int),
                ("basebit", c_int),
                ("base", c_int),
                ("out_params", POINTER(LweParams)),
                ("ks0_raw", POINTER(LweSample)),
                ("ks1_raw", POINTER(POINTER(LweSample))),
                ("ks", POINTER(POINTER(POINTER(LweSample))))]


class LweBootstrappingKey(Structure):
    _fields_ = [("in_out_params", POINTER(LweParams)),
                ("bk_params", POINTER(TGswParams)),
                ("accum_params", POINTER(TLweParams)),
                ("extract_params", POINTER(LweParams)),
                ("bk", POINTER(TGswSample)),
                ("ks", POINTER(LweKeySwitchKey))]


class LagrangeHalfCPolynomial(Structure):
    _fields_ = [("data", POINTER(None)),
                ("precomp", POINTER(None))]


class TLweSampleFFT(Structure):
    _fields_ = [("a", POINTER(LagrangeHalfCPolynomial)),
                ("b", POINTER(LagrangeHalfCPolynomial)),
                ("current_variance", c_double),
                ("k", c_int)]


class TGswSampleFFT(Structure):
    _fields_ = [("all_samples", POINTER(TLweSampleFFT)),
                ("sample", POINTER(POINTER(TLweSampleFFT))),
                ("k", c_int),
                ("l", c_int)]


class LweBootstrappingKeyFFT(Structure):
    _fields_ = [("in_out_params", POINTER(LweParams)),
                ("bk_params", POINTER(TGswParams)),
                ("accum_params", POINTER(TLweParams)),
                ("extract_params", POINTER(LweParams)),
                ("bkFFT", POINTER(TGswSampleFFT)),
                ("ks", POINTER(LweKeySwitchKey))]


class TFheGateBootstrappingCloudKeySet(Structure):
    _fields_ = [("params", POINTER(TFheGateBootstrappingParameterSet)),
                ("bk", POINTER(LweBootstrappingKey)),
                ("bkFFT", POINTER(LweBootstrappingKeyFFT))]


class TFheGateBootstrappingSecretKeySet(Structure):
    _fields_ = [("params", POINTER(TFheGateBootstrappingParameterSet)),
                ("lwe_key", POINTER(LweKey)),
                ("tgsw_key", POINTER(TGswKey)),
                ("cloud", TFheGateBootstrappingCloudKeySet)]

tfhe.new_default_gate_bootstrapping_parameters.argtypes = [c_int]
tfhe.new_default_gate_bootstrapping_parameters.restype = POINTER(TFheGateBootstrappingParameterSet)
tfhe.delete_gate_bootstrapping_parameters.argtypes = [POINTER(TFheGateBootstrappingParameterSet)]
tfhe.delete_gate_bootstrapping_parameters.restype = None
tfhe.new_random_gate_bootstrapping_secret_keyset.argtypes = [POINTER(TFheGateBootstrappingParameterSet)]
tfhe.new_random_gate_bootstrapping_secret_keyset.restype = POINTER(TFheGateBootstrappingSecretKeySet)
tfhe.delete_gate_bootstrapping_secret_keyset.argtypes = [POINTER(TFheGateBootstrappingSecretKeySet)]
tfhe.delete_gate_bootstrapping_secret_keyset.restype = None
tfhe.new_gate_bootstrapping_ciphertext.argtypes = [POINTER(TFheGateBootstrappingParameterSet)]
tfhe.new_gate_bootstrapping_ciphertext.restype = POINTER(LweSample)
tfhe.new_gate_bootstrapping_ciphertext_array.argtypes = [c_int, POINTER(TFheGateBootstrappingParameterSet)]
tfhe.new_gate_bootstrapping_ciphertext_array.restype = POINTER(LweSample) * WIDTH
tfhe.delete_gate_bootstrapping_ciphertext.argtypes = [POINTER(LweSample)]
tfhe.delete_gate_bootstrapping_ciphertext.restype = None
tfhe.delete_gate_bootstrapping_ciphertext_array.argtypes = [c_int, POINTER(LweSample) * WIDTH]
tfhe.delete_gate_bootstrapping_ciphertext_array.restype = None
tfhe_io.export_gate_params.argtypes = [c_char_p, POINTER(TFheGateBootstrappingParameterSet)]
tfhe_io.import_gate_params.argtypes = [c_char_p]
tfhe_io.export_gate_params.restype = None
tfhe_io.import_gate_params.restype = POINTER(TFheGateBootstrappingParameterSet)
tfhe_io.export_secret_keyset.argtypes = [c_char_p, POINTER(TFheGateBootstrappingSecretKeySet)]
tfhe_io.import_secret_keyset.argtypes = [c_char_p]
tfhe_io.export_secret_keyset.restype = None
tfhe_io.import_secret_keyset.restype = POINTER(TFheGateBootstrappingSecretKeySet)
tfhe_io.export_cloud_keyset.argtypes = [c_char_p, POINTER(TFheGateBootstrappingCloudKeySet)]
tfhe_io.import_cloud_keyset.argtypes = [c_char_p]
tfhe_io.export_cloud_keyset.restype = None
tfhe_io.import_cloud_keyset.restype = POINTER(TFheGateBootstrappingCloudKeySet)
tfhe_io.export_ciphertext.argtypes = [c_char_p, POINTER(LweSample), POINTER(TFheGateBootstrappingParameterSet)]
tfhe_io.import_ciphertext.argtypes = [c_char_p, POINTER(LweSample), POINTER(TFheGateBootstrappingParameterSet)]
tfhe_io.import_ciphertext.restype = None

