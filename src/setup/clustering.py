from setup.graph import Graph
import random
from math import sqrt
import pandas as pd
import numpy as np
from sklearn.cluster import spectral_clustering
from setup.load_streets import Map
import os

data_path = os.path.join(os.path.abspath('../..'), 'Data')

def cluster_graph(street_map, number_clusters):
    A = np.array(street_map.get_adj_matrix())
    colors = spectral_clustering(A, n_clusters=number_clusters)

    with open(os.path.join(data_path, 'node_colors.txt'), 'w+') as f:
        for c in colors:
            f.write(str(c)+' ')


def read_colors():
    colors = []
    with open(os.path.join(data_path, 'node_colors.txt'), 'r') as f:
        line = f.read().split(' ')
        for l in line:
            try: colors.append(int(l))
            except ValueError: pass
    return colors


def grid_search(grid, x,y):
    x = int(x)
    y = int(y)

    # Square search
    category = grid[y][x]
    radius = 1
    while category == -1:
        search = []  # A list of locations to search next

        # Add coordinates of 4 sides of square around start coord
        search.extend([(x + 1, y + dy) for dy in range(-radius, radius + 1)])
        search.extend([(x - 1, y + dy) for dy in range(-radius, radius + 1)])
        search.extend([(x + dx, y + 1) for dx in range(-radius, radius + 1)])
        search.extend([(x + dx, y - 1) for dx in range(-radius, radius + 1)])

        for (nx, ny) in search:
            try:
                if grid[ny][nx] != -1:
                    category = grid[ny][nx]
                    break
            except IndexError:
                pass
        radius += 1
    return category



def cluster_crimes(street_map, width, height):

    scale_long = height / (street_map.max_long - street_map.min_long)
    scale_lat = width / (street_map.max_long - street_map.min_long)

    def canvas_coords(lat, long):
        lat -= street_map.min_lat
        long -= street_map.min_long
        lat *= scale_lat
        long *= scale_long
        return lat, long

    colors = read_colors()

    # Create grid
    grid = [[-1 for i in range(width)] for j in range(height)]
    for street in street_map.streets.values():
        for c in street.coords:
            x, y = canvas_coords(*c)
            x = min(x, width - 1)
            y = min(y, height - 1)

            try:
                grid[int(y)][int(x)] = colors[street.node1]
            except IndexError:
                print(int(x), int(y), ' ', c)

    crime_table = open(os.path.join(data_path, 'colored_crimes.csv', 'w+'))
    crime_table.write('LAT,LONG,TIME,COLOR\n')

    data = pd.read_csv(os.path.join(data_path, 'crimes.csv'))

    for i in range(len(data['Lat'])):
        try:
            x, y = canvas_coords(data['Lat'][i], data['Long'][i])
            category = grid_search(grid, x, y)
            crime_table.write(str(data['Lat'][i]) + ',' + \
                              str(data['Long'][i]) + ',' + \
                              data['OCCURRED_ON_DATE'][i] + ',' + \
                              str(category) + '\n')

        except (ValueError, IndexError) as err:
            pass

    crime_table.close()
