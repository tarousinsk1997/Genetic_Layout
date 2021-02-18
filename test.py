import numpy as np
import course

individ = course.Individual()
individ.create_sub_Area()
individ.excelparser()
individ.createSites()

distance = np.ones((12,12))
cargo = np.array(individ.cargo_matrix)
print(np.sum(np.multiply(cargo, distance)) / 2)