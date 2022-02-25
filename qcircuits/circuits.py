import numpy as np
import cirq
import sympy
def measure_all(qubits, n_measurements):
    return [cirq.Z(qubits[i]) for i in range(n_measurements)]
def measure_last(qubits, n_measurements=1):
    return cirq.Z(qubits[-1])

###############################################################
###############################################################
#############    INFORMATION ENCODING CIRCUITS    #############
###############################################################
###############################################################
def simple_encoding_y(circuit, qubits, n_qubits=4):
    print("SIMPLE_ENCODING_Y")
    input_  = sympy.symbols('x:{}'.format(n_qubits))
    for idx, qubit in enumerate(qubits):
        circuit.append(cirq.ry(input_[idx])(qubit))
    print(circuit)
def yz_arccos(circuit, qubits, n_qubits=4):
    print("YZ_ARCCOS")
    input_  = sympy.symbols('x:{}'.format(n_qubits))
    for idx, qubit in enumerate(qubits):
            circuit.append(cirq.ry(input_[idx])(qubit))
            circuit.append(cirq.rz(input_[idx])(qubit))
    print(circuit)
def simple_encoding_z(circuit, qubits, n_qubits=4):
    print("SIMPLE ENCODING_Z")
    input_  = sympy.symbols('x:{}'.format(n_qubits))
    for idx, qubit in enumerate(qubits):
        circuit.append(cirq.H(qubit))
        circuit.append(cirq.rz(input_[idx])(qubit))
    print(circuit)
def simple_encoding_x(circuit, qubits, n_qubits=4):
    print("SIMPLE_ENCODING_X")
    input_  = sympy.symbols('x:{}'.format(n_qubits))
    for idx, qubit in enumerate(qubits):
        circuit.append(cirq.rx(input_[idx])(qubit))
    print(circuit)
def ZZFeatureMap(circuit, qubits, n_qubits=4):
    input_  = sympy.symbols('x:{}'.format(n_qubits))
    for idx, qubit in enumerate(qubits):
        circuit.append(cirq.H(qubit))
        U1 = cirq.ZPowGate(exponent=2*input_[idx])
        circuit.append(U1(qubit))
    for idx in range(n_qubits-1):
        idy = idx + 1;
        circuit.append(cirq.CNOT(qubits[idx], qubits[idy]))
        #v = input_[idx]*input_[idy]
        v = 2*(np.pi - input_[idx])*(np.pi - input_[idy])
        U1 = cirq.ZPowGate(exponent=v)
        circuit.append(U1(qubits[idy]))
        circuit.append(cirq.CNOT(qubits[idx], qubits[idy]))
    print(circuit)
# def ZZFeatureMap(circuit, qubits, n_qubits=4):
#     print("ZZFEATUREMAP")
#     input_  = sympy.symbols('x:{}'.format(n_qubits))
#     for idx, qubit in enumerate(qubits):
#         circuit.append(cirq.H(qubit))
#     for _ in range(2):
#         for idx, qubit in enumerate(qubits):
#             U1 = cirq.ZPowGate(exponent=2*input_[idx])
#             circuit.append(U1(qubit))
#         for idx in range(n_qubits-1):
#             for idy in range(idx+1, n_qubits):
#                 circuit.append(cirq.CNOT(qubits[idx], qubits[idy]))
#                 v = 2*(np.pi - input_[idx])*(np.pi - input_[idy])
#                 U1 = cirq.ZPowGate(exponent=v)
#                 circuit.append(U1(qubits[idy]))
#                 circuit.append(cirq.CNOT(qubits[idx], qubits[idy]))
#     print(circuit)

###############################################################
###############################################################
#############    PARAMETRIZED QUANTUM CIRCUITS    #############
###############################################################
###############################################################
def qc10_pqc(circuit, qubits, n_layers=1, n_qubits=4):
    print("QC10_PQC")
    params  = sympy.symbols('theta:{}'.format(n_qubits*(1+n_layers)))
    for i, qubit in enumerate(qubits):
        #symbol = sympy.Symbol('theta_{}'.format(i+1))
        circuit.append(cirq.ry(params[i])(qubit))
    for layer in range(n_layers):
        for i in range(n_qubits):
            circuit.append(cirq.CZ(qubits[(n_qubits-2-i)%n_qubits], qubits[(n_qubits-1-i)%n_qubits]))
        for i, qubit in enumerate(qubits):
            #symbol = sympy.Symbol('theta_{}'.format(i+1+n_qubits*(layer+1)))
            circuit.append(cirq.ry(params[i+n_qubits*(layer+1)])(qubit))
    print(circuit)
###############################################################################
def generic_pqc(circuit, qubits, n_layers=1, n_qubits=4):
    print("GENERIC_PQC")
    params  = sympy.symbols('theta:{}'.format(6*n_qubits*n_layers))
    for layer in range(n_layers):
        NN_entangler(circuit, qubits)
        for i, qubit in enumerate(qubits):
            n_gate = i+(2*layer)*n_qubits
            n_param = n_gate*3
            U3(params[n_param+0], params[n_param+1], params[n_param+2], circuit, qubit)
        NN2_entangler(circuit, qubits)
        for i, qubit in enumerate(qubits):
            n_gate = i+(2*layer+1)*n_qubits
            n_param = n_gate*3
            U3(params[n_param+0], params[n_param+1], params[n_param+2], circuit, qubit)
    print(circuit)
###############################################################################
def TTN(circuit, qubits, n_layers=None, n_qubits=4):
    print("TTN")
    # n_qubits must be a multiple of 4
    assert (n_qubits%4)==0
    n_layers = int(np.log2(n_qubits))
    param_count = 0
    n_params = int(2**(np.log2(n_qubits)+1)-2 +1) # +1 is for the final gate
    params  = sympy.symbols('theta:{}'.format(n_params))
    for layer in range(n_layers):
        n_gates = n_qubits//(2**(layer+1))
        for idx in range(n_gates):
            qubit0 = idx * (n_qubits//(2**(n_layers-layer-1))) + 2**layer - 1
            qubit1 = idx * (n_qubits//(2**(n_layers-layer-1))) + 2**(layer+1) - 1
            two_qubit_ry(params[param_count], params[param_count+1], circuit, qubits[qubit0], qubits[qubit1])
            param_count += 2
    circuit.append(cirq.ry(params[param_count])(qubits[n_qubits-1]))
###############################################################################
def MPS(circuit, qubits, n_layers=None, n_qubits=4):
    print("MPS")
    # n_qubits must be a multiple of 4
    assert (n_qubits%4)==0
    n_layers = int(n_qubits-1)
    param_count = 0
    n_params = 2*(n_layers) +1 # +1 is for the final gate
    params = sympy.symbols('theta:{}'.format(n_params))
    for layer in range(n_layers):
        two_qubit_ry(params[param_count], params[param_count+1], circuit, qubits[layer], qubits[layer+1])
        param_count += 2
    circuit.append(cirq.ry(params[param_count])(qubits[n_qubits-1]))
###############################################################################
def qc10_pqc_local(circuit, qubits, n_layers=1, n_qubits=4):
    print("QC10_PQC_LOCAL")
    params  = sympy.symbols('theta:{}'.format(n_qubits*(1+n_layers)))
    for i, qubit in enumerate(qubits):
        #symbol = sympy.Symbol('theta_{}'.format(i+1))
        circuit.append(cirq.ry(params[i])(qubit))
    for layer in range(n_layers):
        for i in range(n_qubits):
            circuit.append(cirq.CZ(qubits[(n_qubits-2-i)%n_qubits], qubits[(n_qubits-1-i)%n_qubits]))
        if layer!=(n_layers-1):
            for i, qubit in enumerate(qubits):
                circuit.append(cirq.ry(params[i+n_qubits*(layer+1)])(qubit))
        else:
            circuit.append(cirq.ry(params[n_qubits*(layer+1)])(qubit))
    print(circuit)
###############################################################################
def qc19_pqc(circuit, qubits, n_layers=1, n_qubits=4):
    print("QC19_PQC")
    params  = sympy.symbols('theta:{}'.format(3*n_qubits*n_layers))
    param_count = 0
    for layer in range(n_layers):
        for i, qubit in enumerate(qubits):
            circuit.append(cirq.rx(params[param_count])(qubit))
            param_count += 1
            circuit.append(cirq.rz(params[param_count])(qubit))
            param_count += 1
        for i in range(n_qubits):
            # controlled Rx operations are applied
            # implementation is explained here: https://stackoverflow.com/questions/61852590/how-do-i-implement-a-controlled-rx-in-cirq-tensorflow-quantum
            circuit.append(cirq.CNOT(qubits[(n_qubits-1-i)%n_qubits], qubits[(n_qubits-i)%n_qubits])**(params[param_count]/np.pi))
            param_count += 1
    print(circuit)
###############################################################################
def qc10P_pqc(circuit, qubits, n_layers=1, n_qubits=4):
    print("QC10P_PQC")
    n_params = 2*n_qubits*(1+n_layers)
    params  = sympy.symbols('theta:{}'.format(n_params))
    for i, qubit in enumerate(qubits):
        #symbol = sympy.Symbol('theta_{}'.format(i+1))
        circuit.append(cirq.ry(params[2*i])(qubit))
        circuit.append(cirq.rx(params[2*i+1])(qubit))
    for layer in range(n_layers):
        for i in range(n_qubits):
            circuit.append(cirq.CZ(qubits[(n_qubits-2-i)%n_qubits], qubits[(n_qubits-1-i)%n_qubits]))
        for i, qubit in enumerate(qubits):
            #symbol = sympy.Symbol('theta_{}'.format(i+1+n_qubits*(layer+1)))
            circuit.append(cirq.ry(params[2*i+2*n_qubits*(layer+1)])(qubit))
            circuit.append(cirq.rx(params[2*i+1+2*n_qubits*(layer+1)])(qubit))
    print(circuit)
###############################################################################
def qc6_pqc(circuit, qubits, n_layers=1, n_qubits=4):
    print("QC6_PQC")
    params = sympy.symbols('theta:{}'.format((n_qubits**2 + 3*n_qubits)*n_layers))
    param_count = 0
    for layer in range(n_layers):
        # First Rx-Rz layer
        for i, qubit in enumerate(qubits):
            circuit.append(cirq.rx(params[param_count])(qubit))
            param_count += 1
            circuit.append(cirq.rz(params[param_count])(qubit))
            param_count += 1
        # Apply set of Rx gate (the size of this set is n_qubits)
        for idx in range(n_qubits):
            # Apply Controlled Rx gates (n_qubits-1 times)
            for idy in range(n_qubits-1):
                circuit.append(cirq.CNOT(
                    qubits[(n_qubits-1-idx)%n_qubits],     # Control qubit
                    qubits[(n_qubits-2-idx-idy)%n_qubits]  # Target qubit
                    )**(params[param_count]/np.pi))
                param_count += 1
        # Final Rx-Rz layer
        for i, qubit in enumerate(qubits):
            circuit.append(cirq.rx(params[param_count])(qubit))
            param_count += 1
            circuit.append(cirq.rz(params[param_count])(qubit))
            param_count += 1
    print(circuit)
###############################################################################
############################## SPSA Circuits ##################################
###############################################################################
def SPSA2_PQC(circuit, qubits, n_layers=1, n_qubits=4):
    params  = sympy.symbols('theta:{}'.format(n_qubits*(1+n_layers)))
    for i, qubit in enumerate(qubits):
        #symbol = sympy.Symbol('theta_{}'.format(i+1))
        circuit.append(cirq.ry(np.pi/4.0)(qubit))

    for layer in range(n_layers):
        for i, qubit in enumerate(qubits):
            random_n = np.random.uniform()
            random_rot = np.random.uniform() * 2.0 * np.pi if i != 0 or layer != 0 else params
            if random_n > 2. / 3.:
                # Add a Z.
                circuit.append(cirq.rz(params[2*i])(qubit))
                #circuit.append(cirq.rz(random_rot)(qubit))
            elif random_n > 1. / 3.:
                # Add a Y.
                circuit.append(cirq.ry(params[2*i])(qubit))
                #circuit.append(cirq.ry(random_rot)(qubit))
            else:
                # Add a X.
                circuit.append(cirq.rx(params[2*i])(qubit))
                #circuit.append(cirq.rx(random_rot)(qubit))
    for src, dest in zip(qubits, qubits[1:]):
        circuit.append(cirq.CZ(src, dest))
        
    return circuit

def SPSATEST_PQC(circuit, qubits, n_layers=1, n_qubits=4):
    params = sympy.symbols('theta:{}'.format(n_qubits*(1+n_layers)))
    prep_and_U = SPSA1_PQC(circuit, qubits, n_layers, n_qubits)
    circuit.append(prep_and_U)
    
    U_dagger = (prep_and_U[1:])**-1
    circuit.append(cirq.resolve_parameters(U_dagger, param_resolver={symbol: np.random.uniform() * 2 * np.pi}))
    
    for layer in range(n_layers):
        prep_and_U_circuit = generate_random_qnn(qubits, np.random.uniform() * 2 * np.pi, 4)
        U_circuit = prep_and_U_circuit[1:]
        circuit.append(U_circuit)
        circuit.append(U_circuit**-1)
    print(circuit)

# def SPSA1P_pqc(circuit, qubits, n_layers, n_qubits=4):
#     return 1
###############################################################################
############################## Helper Functions ###############################
###############################################################################
def U3(param0, param1, param2, circuit, qubit):
    circuit.append(cirq.rz(param2)(qubit))
    circuit.append(cirq.rx(np.pi/2)(qubit))
    circuit.append(cirq.rz(param0)(qubit))
    circuit.append(cirq.rx(-np.pi/2)(qubit))
    circuit.append(cirq.rz(param1)(qubit))
###############################################################################
def NN_entangler(circuit, qubits):
        n_qubits = len(qubits)
        for i in range(n_qubits):
                circuit.append(cirq.CNOT(qubits[i%n_qubits], qubits[(i+1)%n_qubits]))
###############################################################################
def NN2_entangler(circuit, qubits):
        n_qubits = len(qubits)
        for i in range(n_qubits):
                circuit.append(cirq.CNOT(qubits[i%n_qubits], qubits[(i+2)%n_qubits]))
###############################################################################
def two_qubit_ry(param0, param1, circuit, qubit0, qubit1):
        circuit.append(cirq.ry(param0)(qubit0))
        circuit.append(cirq.ry(param1)(qubit1))
        circuit.append(cirq.CZ(qubit0, qubit1))
###############################################################################
