import sys
import random
import numpy as np
from copy import deepcopy

import qml
from qml.representations import generate_bob
from qml.kernels import gaussian_kernel
from qml.kernels import laplacian_kernel
from qml.math import cho_solve

def get_wall_times(filename):
  """ returns dic with energies for xyz files
  """
  f = open(filename, "r")
  lines = f.readlines()
  f.close()

  wall_times = dict()

  for line in lines:
    tokens = line.split()
    xyz_name = tokens[0]
    wall_time = float(tokens[1])
    wall_times[xyz_name] = wall_time

  return wall_times

def get_coords(filename):
  """ returns dic with energies for xyz files
  """
  f = open(filename, "r")
  lines = f.readlines()
  f.close()

  coords = dict()

  for line in lines:
    tokens = line.split()
    coord = tokens[0]
    cmd = tokens[1]
    coords[coord] = cmd

  return coords

def get_representation(training_data, prediction_data, path_to_xyz_files):
  """ calculates the representations and stores it in the qml compound class
  """
  mols    = []
  mols_pred = []

  for xyz_file in sorted(training_data.keys()):
    mol = qml.Compound()
    mol.read_xyz(path_to_xyz_files + xyz_file + ".xyz")
    mol.properties = training_data[xyz_file]
    mols.append(mol)

  for xyz_file in sorted(prediction_data.keys()):
    mol = qml.Compound()
    mol.read_xyz(path_to_xyz_files + xyz_file + ".xyz")
    mol.cmd = prediction_data[xyz_file]
    mols_pred.append(mol)

  bags = {
    "H":  max([mol.atomtypes.count("H" ) for mol in mols+mols_pred]),
    "C":  max([mol.atomtypes.count("C" ) for mol in mols+mols_pred]),
    "N":  max([mol.atomtypes.count("N" ) for mol in mols+mols_pred]),
    "O":  max([mol.atomtypes.count("O" ) for mol in mols+mols_pred]),
    "S":  max([mol.atomtypes.count("S" ) for mol in mols+mols_pred]),
    "F":  max([mol.atomtypes.count("F" ) for mol in mols+mols_pred]),
    "Si": max([mol.atomtypes.count("Si") for mol in mols+mols_pred]),
    "P":  max([mol.atomtypes.count("P" ) for mol in mols+mols_pred]),
    "Cl": max([mol.atomtypes.count("Cl") for mol in mols+mols_pred]),
    "Br": max([mol.atomtypes.count("Br") for mol in mols+mols_pred]),
    "Ni": max([mol.atomtypes.count("Ni") for mol in mols+mols_pred]),
    "Pt": max([mol.atomtypes.count("Pt") for mol in mols+mols_pred]),
    "Pd": max([mol.atomtypes.count("Pd") for mol in mols+mols_pred]),
    "Cu": max([mol.atomtypes.count("Cu") for mol in mols+mols_pred]),
    "Ag": max([mol.atomtypes.count("Ag") for mol in mols+mols_pred]),
    "Au": max([mol.atomtypes.count("Au") for mol in mols+mols_pred])
  }

  for mol in mols:
    mol.generate_bob(asize=bags)

  for mol in mols_pred:
    mol.generate_bob(asize=bags)

  return mols, mols_pred

def cross_validation(X, Y, sigmas, llambdas, Ntot):
  """ finds optimal hyperparameters sigma & lambda using cross validation
  """
  parameters = []
  random.seed(666)

  for i in range(len(sigmas)):
    K      = laplacian_kernel(X, X, sigmas[i])

    for j in range(len(llambdas)):
  
      for m in range(5):
        maes = []
        split = range(Ntot)
        random.shuffle(split)

        train = int(len(split)*0.8)
        test  = int(Ntot - train)

        training_index  = split[:train]
        test_index      = split[-test:]

        y_train = Y[training_index]
        y_test  = Y[test_index]

        C = deepcopy(K[training_index][:,training_index])
        C[np.diag_indices_from(C)] += llambdas[j]

        alpha = cho_solve(C, y_train)

        y_est = np.dot((K[training_index][:,test_index]).T, alpha)

        diff = y_est  - y_test
        mae = np.mean(np.abs(diff))
        maes.append(mae)

      parameters.append([llambdas[j], sigmas[i], np.mean(maes)])

  maes = [mae[2] for mae in parameters]
  index = maes.index(min(maes))

  return parameters[index][0], parameters[index][1]

if __name__ == "__main__":
  # cmd arguments
  training_data_file = sys.argv[1]
  test_data_file   = sys.argv[2]
  path_to_xyz_files  = sys.argv[3]

  # read in data
  training_data    = get_wall_times(training_data_file)
  prediction_data = get_coords(test_data_file)

  # lists og  parameters
  Ntot = len(training_data)
  llambdas = [ 1e-3, 1e-5, 1e-7, 1e-9]
  sigmas  = [0.1*2**i for i in range(5,20)]

  # calculate BoB representation
  mols, mols_pred = get_representation(training_data, prediction_data, path_to_xyz_files)

  # save representations (X, X_test) and properties (Y, Y_test) in np arrays
  X      = np.asarray([mol.representation for mol in mols])
  X_pred = np.asarray([mol.representation for mol in mols_pred])
  Y      = np.asarray([mol.properties for mol in mols])

  # get optimal hyperparameters
  llambda, sigma = cross_validation(X, Y, sigmas, llambdas, Ntot)

  # calculate laplacian kernel
  K      = laplacian_kernel(X, X,      sigma)
  K_pred = laplacian_kernel(X, X_pred, sigma)

  # get regression coefficients alhpa
  C = deepcopy(K)
  C[np.diag_indices_from(C)] += llambda

  alpha = cho_solve(C, Y)

  # make predictions
  Yss = np.dot(K_pred.T, alpha)

  for i in range(len(Yss)):
    print(Yss[i], mols_pred[i].cmd)
