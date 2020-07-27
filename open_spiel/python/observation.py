# Copyright 2019 DeepMind Technologies Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An observation of a game.

This is intended to be the main way to get observations of states in Python.
The usage pattern is as follows:

0. Create the game we will be playing
1. Create observation objects for each kind of observation required.
2. Every time an observation is required, call:
      `observation.set_from(state, player)`
   The tensor contained in the Observation class will be updated with an
   observation of the supplied state. This tensor is updated in-place, so if
   you wish to retain it, you must make a copy.

The following options are available when creating an Observation:
 - perfect_recall: if true, each observation must allow the observing player to
   reconstruct their history of actions and observations.
 - public_info: if true, the observation should include public information
 - private_info: specifies for which players private information should be
   included - all players, the observing player, or no players
 - params: game-specific parameters for observations

We ultimately aim to have all games support all combinations of these arguments.
However, initially many games will only support the combinations corresponding
to ObservationTensor and InformationStateTensor:
 - ObservationTensor: perfect_recall=False, public_info=True,
   private_info=SinglePlayer
 - InformationStateTensor: perfect_recall=True, public_info=True,
   private_info=SinglePlayer

Three formats of observation are supported:
a. 1-D numpy array, accessed by `observation.tensor`
b. Dict of numpy arrays, accessed by `observation.dict`. These are pieces of the
   1-D array, reshaped. The np.array objects refer to the same memory as the
   1-D array (no copying!).
c. String, hopefully human-readable (primarily for debugging purposes)

For usage examples, see `observation_test.py`.
"""

import numpy as np

import pyspiel


class _Observation:
  """Contains an observation from a game."""

  def __init__(self, game, imperfect_information_observation_type, params):
    obs = game.make_observer(imperfect_information_observation_type, params)
    self._observation = pyspiel._Observation(game, obs)
    self.tensor = np.frombuffer(self._observation, np.float32)
    self.dict = {}
    offset = 0
    for tensor_info in self._observation.tensor_info():
      size = np.product(tensor_info.shape)
      values = self.tensor[offset:offset + size].reshape(tensor_info.shape)
      self.dict[tensor_info.name] = values
      offset += size

  def set_from(self, state, player):
    self._observation.set_from(state, player)

  def string_from(self, state, player):
    return self._observation.string_from(state, player)


def make_observation(game,
                     imperfect_information_observation_type=None,
                     params=None):
  return _Observation(game, imperfect_information_observation_type, params or
                      {})