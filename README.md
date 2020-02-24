![stable](http://badges.github.io/stability-badges/dist/stable.svg)
# Nodal-NEAT

The NEAT algorithm by K.Stanley written from nodes instead of the traditional connection genes. This allows tracking how nodes are added using a metric called 'split depth' in the nuclei.py module and 'primal nodes' which represent the nodal skeleton structure of a topology. Integrating simplification in crossover allows genomes to drop sequences of node splits, sampling simplicity at designated localities in the neural network topology based on the evolutionary route taken through the fitness landscape. This approach also allows sampling larger steps of complexification during crossover.

(see NEAT phased pruning for a similar but connnection oriented and non-crossover approach to simplification)

Please feel free to contact me with questions.
