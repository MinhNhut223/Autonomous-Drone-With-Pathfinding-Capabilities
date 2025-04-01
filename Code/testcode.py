import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import heapq

def load_image():
    global img, img_display, img_binary, img_buffered
    
    file_path = filedialog.askopenfilename(filetypes=[("PGM files", "*.pgm")])
    if file_path:
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            messagebox.showerror("Error", "File could not be loaded. Please select a valid PGM file.")
            return
        
        # Resize image to 500x500
        img = cv2.resize(img, (500, 500))
        
        if len(img.shape) == 2:
            # Image is already grayscale (2D), no need to convert
            img_binary = img
        else:
            # Apply a threshold to create binary image
            _, img_binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        
        # Create a buffer zone by dilating the binary image
        kernel = np.ones((3, 3), np.uint8)
        img_buffered = cv2.dilate(img_binary, kernel, iterations=1)
        
        # Convert img_display to BGR for displaying in OpenCV window
        img_display = cv2.cvtColor(img_buffered, cv2.COLOR_GRAY2BGR)
        
        # Display image using OpenCV
        cv2.imshow("Image", img_display)
        
        # Set mouse callback function
        cv2.setMouseCallback("Image", on_mouse_click)

def on_mouse_click(event, x, y, flags, param):
    global start_point, end_point, img_buffered, img_display
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if start_point is None:
            if img_buffered[y, x] != 255:
                messagebox.showerror("Error", "Start point must be on a white pixel (value 0). Please select another point.")
                return
            start_point = (y, x)
            cv2.circle(img_display, (x, y), 3, (0, 255, 0), -1)  # Vẽ đường với bán kính 3 pixel
            cv2.imshow("Image", img_display)
            
        elif end_point is None:
            if img_buffered[y, x] != 255:
                messagebox.showerror("Error", "End point must be on a white pixel (value 0). Please select another point.")
                return
            end_point = (y, x)
            cv2.circle(img_display, (x, y), 3, (0, 0, 255), -1)  # Vẽ đường với bán kính 3 pixel
            cv2.imshow("Image", img_display)
            
        if start_point and end_point:
            find_path()

def find_path():
    global img_binary, start_point, end_point, img_display
    path = a_star(img_binary, start_point, end_point)
    if path:
        for y, x in path:
            # Đảm bảo đường đi không trùng với màu đen và cách tường một khoảng
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= y + i < img_binary.shape[0] and 0 <= x + j < img_binary.shape[1]:
                        if img_binary[y + i, x + j] != 255:
                            continue
                        img_display[y + i, x + j] = [0, 0, 255]
        cv2.imshow("Image", img_display)
    else:
        messagebox.showinfo("Error", "No path found!")


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(map_matrix, start, goal):
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
            if 0 <= neighbor[0] < map_matrix.shape[0]:
                if 0 <= neighbor[1] < map_matrix.shape[1]:
                    if map_matrix[neighbor[0]][neighbor[1]] != 255:
                        continue
                else:
                    continue
            else:
                continue
            
            tentative_g_score = gscore[current] + 1
            
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
            
            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
                
    return False

# Initialize variables
img = None
img_display = None
img_binary = None
img_buffered = None
start_point = None
end_point = None

# Create the GUI
root = tk.Tk()
root.title("Path Finder")

load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.pack()

root.mainloop()

# Close OpenCV windows when the program exits
cv2.destroyAllWindows()
