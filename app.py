import pygame
import numpy as np

WINDOW_SIZE = 800
ROTATE_SPEED = 0.01
window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
clock = pygame.time.Clock()

scale = 100
angle_x = angle_y = angle_z = 0

object_material = np.array([255,255,255])
light_direction = np.array([0, 0, -1])  # Light coming from the viewer's direction

def multiply_m(a, b):
    return np.dot(a, b)

def project_point(point):
    x = (point[0] * scale) + WINDOW_SIZE / 2
    y = (point[1] * scale) + WINDOW_SIZE / 2
    return (x, y)

def draw_face(face, points, color):
    pygame.draw.polygon(window, color, [points[i] for i in face])

def connect_points(i, j, points):
    pygame.draw.line(window, (25, 25, 25), points[i], points[j])

def load_obj(filename):
    vertices = []
    faces = []
    
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v '):
                parts = line.strip().split()
                vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                vertices.append(vertex)
            elif line.startswith('f '):
                parts = line.strip().split()
                face = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                faces.append(face)
    
    return np.array(vertices), faces

def calculate_normal(face, vertices):
    v1 = vertices[face[1]] - vertices[face[0]]
    v2 = vertices[face[2]] - vertices[face[0]]
    normal = np.cross(v1, v2)
    normal = normal / np.linalg.norm(normal)
    return normal

model_vertices, model_faces = load_obj('models/monkey.obj')

edges = set()
for face in model_faces:
    for i in range(len(face)):
        edge = (face[i], face[(i + 1) % len(face)])
        if edge not in edges and (edge[1], edge[0]) not in edges:
            edges.add(edge)
edges = list(edges)

draw_edges = False
mouse_x, mouse_y = pygame.mouse.get_pos()

while True:
    clock.tick(60)
    window.fill((0, 0, 0))

    new_mouse_x, new_mouse_y = pygame.mouse.get_pos()
    mouse_dx = new_mouse_x - mouse_x
    mouse_dy = new_mouse_y - mouse_y

    angle_x -= mouse_dy * ROTATE_SPEED
    angle_y += mouse_dx * ROTATE_SPEED

    mouse_x, mouse_y = new_mouse_x, new_mouse_y

    cos_x, sin_x = np.cos(angle_x), np.sin(angle_x)
    cos_y, sin_y = np.cos(angle_y), np.sin(angle_y)
    cos_z, sin_z = np.cos(angle_z), np.sin(angle_z)

    rotation_x = np.array([
        [1, 0, 0],
        [0, cos_x, -sin_x],
        [0, sin_x, cos_x]
    ])

    rotation_y = np.array([
        [cos_y, 0, sin_y],
        [0, 1, 0],
        [-sin_y, 0, cos_y]
    ])

    rotation_z = np.array([
        [cos_z, -sin_z, 0],
        [sin_z, cos_z, 0],
        [0, 0, 1]
    ])

    transformed_vertices = []
    for vertex in model_vertices:
        rotated_vertex = multiply_m(rotation_x, vertex)
        rotated_vertex = multiply_m(rotation_y, rotated_vertex)
        rotated_vertex = multiply_m(rotation_z, rotated_vertex)
        transformed_vertices.append(rotated_vertex)
    
    transformed_vertices = np.array(transformed_vertices)
    
    points = [project_point(v) for v in transformed_vertices]

    face_data = []
    for face in model_faces:
        avg_depth = np.mean([transformed_vertices[i][2] for i in face])
        normal = calculate_normal(face, transformed_vertices)
        brightness = np.dot(normal, light_direction)
        brightness = max(0, brightness)  # Clamp to [0, 1]
        shaded_color = (object_material * brightness).astype(int)
        face_data.append((face, avg_depth, shaded_color))

    face_data.sort(key=lambda f: f[1], reverse=True)

    for face, _, color in face_data:
        draw_face(face, points, color)

    if draw_edges:
        for edge in edges:
            connect_points(edge[0], edge[1], points)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                draw_edges = not draw_edges

    pygame.display.update()
