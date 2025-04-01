import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import heapq

def load_image():
    global img, img_display, img_gray, img_binary
    file_path = filedialog.askopenfilename(filetypes=[("PGM files", "*.pgm")])
    if file_path:
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            messagebox.showerror("Error", "File could not be loaded. Please select a valid PGM file.")
            return
        
        # Convert img to img_binary based on the specified condition
        img_binary = np.where(img == 255, 0, 1).astype(np.uint8)
        
        img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        cv2.imshow("Image", img_display)
        cv2.setMouseCallback("Image", on_mouse_click)


def on_mouse_click(event, x, y, flags, param):
    global start_point, end_point
    if event == cv2.EVENT_LBUTTONDOWN:
        if start_point is None:
            start_point = (y, x)
            cv2.circle(img_display, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Image", img_display)
        elif end_point is None:
            end_point = (y, x)
            cv2.circle(img_display, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Image", img_display)
        if start_point and end_point:
            find_path()

def find_path():
    global img_binary, start_point, end_point, img_display
    path = dijkstra(img_binary, start_point, end_point)
    if path:
        for y, x in path:
            img_display[y, x] = [0, 255, 255]
        cv2.imshow("Image", img_display)
    else:
        messagebox.showinfo("Error", "No path found!")

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import heapq

def load_image():
    global img, img_display, img_gray, img_binary
    file_path = filedialog.askopenfilename(filetypes=[("PGM files", "*.pgm")])
    if file_path:
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            messagebox.showerror("Error", "File could not be loaded. Please select a valid PGM file.")
            return
        
        # Resize image to 500x500
        img = cv2.resize(img, (500, 500))
        
        # Convert img to img_binary based on the specified condition
        img_binary = np.where(img == 255, 0, 1).astype(np.uint8)
        
        img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        cv2.imshow("Image", img_display)
        cv2.setMouseCallback("Image", on_mouse_click)



def on_mouse_click(event, x, y, flags, param):
    global start_point, end_point, img_binary, img_display
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if start_point is None:
            if img_binary[y, x] != 0:
                messagebox.showerror("Error", "Start point must be on a white pixel (value 0). Please select another point.")
                return
            start_point = (y, x)
            cv2.circle(img_display, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Image", img_display)
            
        elif end_point is None:
            if img_binary[y, x] != 0:
                messagebox.showerror("Error", "End point must be on a white pixel (value 0). Please select another point.")
                return
            end_point = (y, x)
            cv2.circle(img_display, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Image", img_display)
            
        if start_point and end_point:
            find_path()


def find_path():
    global img_binary, start_point, end_point, img_display
    path = dijkstra(img_binary, start_point, end_point)
    if path:
        for y, x in path:
            img_display[y, x] = [0, 255, 255]
        cv2.imshow("Image", img_display)
    else:
        messagebox.showinfo("Error", "No path found!")

def dijkstra(map_matrix, start, goal):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    paths = []
    min_path = None
    min_zeros = float('inf')

    def reconstruct_path(came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def get_num_zeros(path):
        num_zeros = 0
        for p in path:
            if map_matrix[p[0], p[1]] == 0:
                num_zeros += 1
        return num_zeros

    def explore_neighbors(current, gscore, came_from, oheap):
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < map_matrix.shape[0] and 0 <= neighbor[1] < map_matrix.shape[1]:
                if map_matrix[neighbor[0], neighbor[1]] != 0:
                    continue
            else:
                continue

            tentative_g_score = gscore[current] + 1
            if neighbor in gscore and tentative_g_score >= gscore[neighbor]:
                continue

            came_from[neighbor] = current
            gscore[neighbor] = tentative_g_score
            fscore = tentative_g_score + heuristic(neighbor, goal)
            heapq.heappush(oheap, (fscore, neighbor))

    oheap = []
    heapq.heappush(oheap, (0, start))
    came_from = {}
    gscore = {start: 0}

    while oheap:
        current = heapq.heappop(oheap)[1]

        if current == goal:
            path = reconstruct_path(came_from, current)
            num_zeros = get_num_zeros(path)
            paths.append((path, num_zeros))
            if num_zeros < min_zeros:
                min_zeros = num_zeros
                min_path = path
            continue

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < map_matrix.shape[0] and 0 <= neighbor[1] < map_matrix.shape[1]:
                if map_matrix[neighbor[0], neighbor[1]] != 0:
                    continue
            else:
                continue

            tentative_g_score = gscore[current] + 1
            if neighbor in gscore and tentative_g_score >= gscore[neighbor]:
                continue

            came_from[neighbor] = current
            gscore[neighbor] = tentative_g_score
            fscore = tentative_g_score + heuristic(neighbor, goal)
            heapq.heappush(oheap, (fscore, neighbor))

    return min_path

# Khởi tạo các biến
img = None
img_display = None
img_gray = None
img_binary = None
start_point = None
end_point = None

# Tạo giao diện người dùng
root = tk.Tk()
root.title("Path Finder")

load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.pack()

root.mainloop()

# Đóng cửa sổ OpenCV khi thoát chương trình
cv2.destroyAllWindows()


# Khởi tạo các biến
img = None
img_display = None
img_gray = None
img_binary = None
start_point = None
end_point = None

# Tạo giao diện người dùng
root = tk.Tk()
root.title("Path Finder")

load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.pack()

root.mainloop()

# Đóng cửa sổ OpenCV khi thoát chương trình
cv2.destroyAllWindows()
