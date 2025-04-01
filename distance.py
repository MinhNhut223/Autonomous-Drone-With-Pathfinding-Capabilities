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
        _, img_binary = cv2.threshold(img, 128, 1, cv2.THRESH_BINARY_INV)
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

def dijkstra(map_matrix, start, goal):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []

    heapq.heappush(oheap, (fscore[start], start))
    
    while oheap:
        current = heapq.heappop(oheap)[1]
        
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            data.append(start)
            return data[::-1]
        
        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + 1
            if 0 <= neighbor[0] < map_matrix.shape[0]:
                if 0 <= neighbor[1] < map_matrix.shape[1]:                
                    if map_matrix[neighbor[0]][neighbor[1]] == 0:
                        continue
                else:
                    continue
            else:
                continue
                
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
                
            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
                
    return None

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
