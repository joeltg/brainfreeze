#include <stdio.h>
#include <tfhe/tfhe.h>
#include <tfhe/tfhe_io.h>


/** Gate parameters */

void export_gate_params(const char* filename, const TFheGateBootstrappingParameterSet* params) {
    FILE* file = fopen(filename, "w");
    export_tfheGateBootstrappingParameterSet_toFile(file, params);
    fclose(file);
}

TFheGateBootstrappingParameterSet* import_gate_params(const char* filename) {
    FILE* file = fopen(filename, "r");
    TFheGateBootstrappingParameterSet* params = new_tfheGateBootstrappingParameterSet_fromFile(file);
    fclose(file);
    return params;
}


/** Secret keysets */

void export_secret_keyset(const char* filename, const TFheGateBootstrappingSecretKeySet* params) {
    FILE* file = fopen(filename, "w");
    export_tfheGateBootstrappingSecretKeySet_toFile(file, params);
    fclose(file);
}

TFheGateBootstrappingSecretKeySet* import_secret_keyset(const char* filename) {
    FILE* file = fopen(filename, "r");
    TFheGateBootstrappingSecretKeySet* keyset = new_tfheGateBootstrappingSecretKeySet_fromFile(file);
    fclose(file);
    return keyset;
}


/** Cloud keysets */

void export_cloud_keyset(const char* filename, const TFheGateBootstrappingCloudKeySet* params) {
    FILE* file = fopen(filename, "w");
    export_tfheGateBootstrappingCloudKeySet_toFile(file, params);
    fclose(file);
}

TFheGateBootstrappingCloudKeySet* import_cloud_keyset(const char* filename) {
    FILE* file = fopen(filename, "r");
    TFheGateBootstrappingCloudKeySet* keyset = new_tfheGateBootstrappingCloudKeySet_fromFile(file);
    fclose(file);
    return keyset;
}


/** Ciphertexts */

void export_ciphertext (const char* filename, const LweSample* sample, const TFheGateBootstrappingParameterSet* params) {
    FILE* file = fopen(filename, "w");
    export_gate_bootstrapping_ciphertext_toFile(file, sample, params);
    fclose(file);
}

void import_ciphertext(const char* filename, LweSample* sample, const TFheGateBootstrappingParameterSet* params) {
    FILE* file = fopen(filename, "r");
    import_gate_bootstrapping_ciphertext_fromFile(file, sample, params);
    fclose(file);
}

