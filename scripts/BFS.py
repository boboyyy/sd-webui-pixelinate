import time

import random

from PIL import Image
import numpy as np
from queue import Queue

random.seed(-1)
def rgb_distance(pixel1, pixel2):
    return np.linalg.norm(np.array(pixel1, dtype=float) - np.array(pixel2, dtype=float))


def bfs(img, visited, i, j, n):
    height, width, _ = img.shape
    group = []
    q = Queue()
    q.put((i, j))
    while not q.empty():
        x, y = q.get()
        if 0 <= x < height and 0 <= y < width and not visited[x][y]:
            visited[x][y] = True
            group.append((x, y))
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < height and 0 <= ny < width and not visited[nx][ny]:
                        if rgb_distance(img[x][y], img[nx][ny]) < n:
                            q.put((nx, ny))

    return group


def process_image(img, n):
    height, width, _ = img.shape
    visited = [[False for _ in range(width)] for _ in range(height)]
    groups = []
    for i in range(height):
        for j in range(width):
            if not visited[i][j]:
                group = bfs(img, visited, i, j, n)
                if group:
                    groups.append(group)

    # 后处理：计算每个组的颜色均值，并更新原图
    for group in groups:
        total_r, total_g, total_b = 0, 0, 0
        for x, y in group:
            total_r += img[x][y][0]
            total_g += img[x][y][1]
            total_b += img[x][y][2]
        avg_r = int(total_r / len(group))
        avg_g = int(total_g / len(group))
        avg_b = int(total_b / len(group))

        if False:
            random_color = [random.randint(0, 254), random.randint(0, 254), random.randint(0, 254)]
            for x, y in group:
                img[x][y] = random_color
        else:
            for x, y in group:
                img[x][y] = [avg_r, avg_g, avg_b]
    return img

def bfs_full(img_path, threshold=30):
    img = Image.open(img_path)
    result_img = process_image(np.array(img), threshold)
    return result_img


