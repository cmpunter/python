#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Nelder-Mead algorithm 
reference: https://en.wikipedia.org/wiki/Nelder%E2%80%93Mead_method

Copyright (C) 2019 C.M. Punter (cmpunter@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import math


def minimize(fun, initial, delta=0.1, alpha=1, gamma=2, rho=0.5, sigma=0.5, tolerance=1e-8, max_iterations=500):
	"""this function minimizes a given function fun
	Args:
		fun (function): The function that need to be minimized
		initial: Initial guess for the function parameters
	"""
	
	# initialize all vertices
	vertices = [initial]
	
	for i in range(len(initial)):
		vertices.append(initial[:i] + (initial[i] + delta,) + initial[i + 1:])

	iteration = 0
	
	while True:
		# (1) order
		vertices.sort(key = lambda p: fun(*p))

		if fun(*vertices[-1]) - fun(*vertices[0]) < tolerance or iteration >= max_iterations:
			return vertices[0]

		iteration += 1
		
		# (2) calculate centroid
		centroid = tuple([sum(p) / len(p) for p in zip(*vertices[:-1])])
		
		# (3) reflection
		reflected = tuple([c + alpha * (c - w) for c, w in zip(centroid, vertices[-1])])
	
		# test if reflected point is better than the second worst, but not better than the best
		if fun(*vertices[-2]) > fun(*reflected) > fun(*vertices[0]):
			vertices[-1] = reflected
		else:
			# test if reflected point is the best point so far
			if fun(*reflected) < fun(*vertices[0]):
				expanded = tuple([c + gamma * (r - c) for c, r in zip(centroid, reflected)])
	
				# test if the expanded point is better than the reflected point
				if fun(*expanded) < fun(*reflected):
					vertices[-1] = expanded
				else:
					vertices[-1] = reflected
			else:
				
				# (4) contraction
				contracted = tuple([c + rho * (w - c) for c, w in zip(centroid, vertices[-1])])
	
				# test if the contracted point is better than the worst point
				if fun(*contracted) < fun(*vertices[-1]):
					vertices[-1] = contracted
				else:
					# (6) shrink
					vertices = [vertices[0]] + [tuple([b + sigma * (p - b) for b, p in zip(v, vertices[0])]) for v in vertices[1:]]

	
def rosenbrock(x, y):
	return 100 * math.pow(y - math.pow(x, 2), 2) + math.pow(1 - x, 2)


p = minimize(rosenbrock, (10, 10))
print(p)
