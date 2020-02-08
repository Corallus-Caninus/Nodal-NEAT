![stability-wip](https://img.shields.io/badge/stability-work_in_progress-blue.svg)

# Nodal-NEAT

The NEAT algorithm by K.Stanley written from nodes instead of the traditional connection genes. This allows tracking how nodes are added using a metric called 'split depth' in the chromosome.py module and 'primal nodes' which represent the nodal 'skeleton' structure of a topology. This is useful for performing meaningful crossover that scales with genome dissimalarity. Split depth also creates a 'moving average sliding window' throughout the complexification process. Integrating simplification in crossover allows genomes to drop sequences of node splits and sample simplicity at designated localities in the neural network topology under guidance of the genetic algorithm as well as sample larger steps of complexification.

(see NEAT phased pruning for a similar but connnection oriented and non-crossover approach to simplification)

Please feel free to contact me with questions.
