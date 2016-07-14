from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from os import remove, stat
from os.path import exists, join
from skimage.measure import compare_ssim
from string import ascii_uppercase, digits
import pickle
from time import sleep
from render_server import TARGET_FILENAME
from PIL import Image
from datetime import datetime
from math import pi
from random import random, choice, randint
from numpy import asarray, mean, std, arange, histogram, int8
from numpy import min as num_min
import warnings

TARGET = asarray(Image.open(TARGET_FILENAME).convert('RGB')).astype(int8)

TARGET_HIST_1 = histogram(TARGET[:][:][0], bins=arange(0, 256))[0]
TARGET_HIST_2 = histogram(TARGET[:][:][1], bins=arange(0, 256))[0]
TARGET_HIST_3 = histogram(TARGET[:][:][2], bins=arange(0, 256))[0]

OBJECTS = ['Box', 'Pyramid', 'Arrow', 'Cone', 'Cylinder', 'Ellipsoid', 'Ring']
COLORS = ['RED', 'GREEN', 'GRAY', 'MAGENTA', 'ORANGE', 'BLUE', 'BLACK', 'YELLOW']

# let's do up to 10 operations
IND_INIT_SIZE = 20
# create a list of all possible operations
ITEMS = []
for _object in OBJECTS:
    for _color in COLORS:
        for x in arange(-3, 3, 0.2):
            for y in arange(-3, 3, 0.2):
                for s in arange(0.1, 3, 0.2):
                    ind_object = {'primitive': _object, 'color': _color, 'x': x,
                                  'y':y, 's': s}
                    #print(ind_object)
                    ITEMS.append({'op': ind_object, 'name': str(_object)})


def mate_operations(ind1, ind2, indpb):
    """Swaps the operations between lists of operations"""
    for i in range(0, min(len(ind1), len(ind2))):
        if random() < indpb:
            ind1[i], ind2[i] = ind2[i], ind1[i]
    return ind1, ind2


def mutate_operations(individual):
    """Adds or remove an item from an individual"""
    if random() > 0.5:
        individual.append(choice(ITEMS))
    else:
        val = randint(0, len(individual)-1)
        del individual[val]
    return individual,

def alternate_compare(array_in):
    '''
    hist1 = histogram(array_in[:][:][0], bins=arange(0, 256))[0]
    hist2 = histogram(array_in[:][:][1], bins=arange(0, 256))[0]
    hist3 = histogram(array_in[:][:][2], bins=arange(0, 256))[0]
    diff = sum(abs(TARGET_HIST_1-hist1))+sum(abs(TARGET_HIST_2-hist2))+sum(abs(
        TARGET_HIST_3-hist3))
    '''
    array_in = array_in.astype(int8)
    '''
    diff = 0
    for x in range(0, array_in.shape[0]):
        for y in range(0, array_in.shape[1]):
            for pix in range(0, 3):
                diff += abs(array_in[x][y][pix] - TARGET[x][y][pix])
    '''
    diff = abs(sum(abs(array_in.flatten() - TARGET.flatten())))
    return -diff

def eval_sol(operations):
    # generate a random string for the name
    N = 10
    comparison = 100000000
    _filename = ''.join(choice(ascii_uppercase + digits) for _ in range(N))
    _image_filename = simulate1(_filename)
    read_image_in = False
    while not read_image_in:
        try:
            generated = asarray(Image.open(_image_filename).convert('RGB'))
            read_image_in = True
        except Exception as e:
            #print(e, _image_filename)
            pass
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        comparison = alternate_compare(generated)
        if comparison == 0:
            print("file "+_filename+" was perfect")
    #remove(_image_filename)
    return (-comparison,)

creator.create("FitnessMin", base.Fitness, weights=(-4.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_item", choice, ITEMS)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_item, IND_INIT_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", eval_sol)
toolbox.register("mate", mate_operations, indpb=0.5)
toolbox.register("mutate", mutate_operations)
toolbox.register("select", tools.selNSGA2)


def simulate1(_filename="output"):
    operations = []
    for i in range(0, IND_INIT_SIZE):
        operations.append(choice(ITEMS))
    dump_file(operations, _filename)
    _image_filename = join("to_render", _filename + ".png")
    while not exists(_image_filename):
        pass
    while stat(_image_filename).st_size == 0:
        pass
    return _image_filename

def dump_file(operations, _filename):
    try:
        _pickle_file = join("to_render", _filename + ".pickle")
    except Exception:
        print(type(_filename), _filename)
    pickle.dump(operations, open(_pickle_file, "wb"))


def main():
    NGEN = 4
    MU = 10
    LAMBDA = 200
    CXPB = 0.3
    MUTPB = 0.6
    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()

    stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    stats.register("avg", mean, axis=0)
    stats.register("std", std, axis=0)
    stats.register("min", num_min, axis=0)
    #stats.register("best", pop., axis=0)

    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
                              stats, halloffame=hof)
    for i in range(0, len(hof)):
        dump_file(hof[i][-1], "best_gen_"+str(i))
    print(dir(hof[-1][-1]))
    return pop, stats, hof


if __name__ == "__main__":
    ga_results = main()
    parts = []
    for op in ga_results[2][-1]:
        parts.append(op['name'])
    results = simulate1(ga_results[2][-1])
    print("fitness: "+str(results))
    filename = datetime.now().strftime("solution_%Y-%m-%d_%H:%M:%S.svg")
    caption = "Fidelity: 00({:.3}) 01({:.3}) 10({:.3}) 11({:.3}) ".format(
        results['state00'], results['state01'], results['state10'], results[
            'state11'])
