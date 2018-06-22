Examples
========

Local Search
------------

::

 """This script uses shadho to minimize the sin function over domain [0, 2*pi]
 """

  # Imports from shadho:
  #   - Shadho is the main driver class
  #   - rand contains helper functions to define search spaces
  from shadho import Shadho, rand

  import math

  
  # The objective function is defined here.
  # It accepts one input, a dictionary containing the supplied parameter values,
  # and returns the floating point value sin(x). 
  def obj(params):
      # Note that x is stored in the params dictionary.
      # shadho does not unpack or flatten parameter values. 
      return math.sin(params['x'])
  
  # The objective function must return either a single floating point value, or
  # else a dictionary with 'loss' as a key with a floating point value at a minimum.
  
  # Here, we define the search space: a uniform distribution over [0, 2*pi]
  space = {
      'x': rand.uniform(0.0, 2.0 * math.pi)
  }
  
  
  if __name__ == '__main__':
      # The shadho driver is created here, then configured
      # test hyperparameters on the local machine.
      opt = Shadho(obj, space, timeout=60)
      opt.config['global']['manager'] = 'local'
      opt.run()
  
  # After shadho is finished, it prints out the optimal loss and hyperparameters.
  # A database (shadho.json) containing the records of all is also saved to the 
  # working directory.   
  

Distributed Search
------------------

sin.py

::

  # shadho sends a small module along with every worker that can wrap the
  # objective function. Start by importing this module.
  import shadho_worker
  
  # shadho_run_task automatically loads hyperparameter values and saves
  # the resulting output in a format that shadho knows to look for. All
  # you have to do is write a function that takes the parameters as
  # an argument.
  
  import math
  
  # The objective function is defined here (same code as in ex1)
  def opt(params):
      return math.sin(params['x'])
  
  if __name__ == '__main__':
      # To run the worker, just pass the objective function to shadho_worker.run 
      shadho_worker.run(opt)

wq_sin.py

::

  """This script runs the hyperparameter search on remote workers.
  """
  
  # These are imported, same as before
  from shadho import Shadho, rand
  
  import math
  
  
  # The space is also defined exactly the same.
  space = {
      'x': rand.uniform(0.0, 2.0 * math.pi)
  }
  
  
  if __name__ == '__main__':
      # This time, instead of configuring shadho to run locally,
      # we direct it to the input files that run the optimization task.
  
      # Instead of the objective function, shadho is given a command that gets
      # run on the remote worker.
      opt = Shadho('bash run_sin.sh', space, timeout=60)
      
      # Two input files are also added: the first is run directly by the worker
      # and can be used to set up your runtime environment (module load, anyone?)
      # The second is the script we're trying to optimize.
      opt.add_input_file('run_sin.sh')
      opt.add_input_file('sin.py')
      opt.run()

