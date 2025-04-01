import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import heapq


def load_image():
    global img, img_resized, img_display, img_binary, img_buffered, start_point, end_point
    
    file_path = filedialog.askopenfilename(filetypes=[("PGM files", "*.pgm")])
    if file_path:
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            messagebox.showerror("Error", "File could not be loaded. Please select a valid PGM file.")
            return
        
        start_point = None
        end_point = None

        img_resized = cv2.resize(img, (500, 500))
        
        _, img_binary = cv2.threshold(img_resized, 127, 255, cv2.THRESH_BINARY)
        
        kernel = np.ones((3, 3), np.uint8)
        img_buffered = cv2.dilate(img_binary, kernel, iterations=1)
        
        img_display = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2BGR)
        
        cv2.imshow("Image", img_display)
        
        cv2.setMouseCallback("Image", on_mouse_click)

def on_mouse_click(event, x, y, flags, param):
    global start_point, end_point, img_resized, img_display
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if start_point is None:
            if img_buffered[y, x] != 255:
                messagebox.showerror("Error", "Start point must be on a white pixel (value 0). Please select another point.")
                return
            start_point = (y, x)
            cv2.circle(img_display, (x, y), 3, (0, 255, 0), -1)
            cv2.imshow("Image", img_display)
            
        elif end_point is None:
            if img_buffered[y, x] != 255:
                messagebox.showerror("Error", "End point must be on a white pixel (value 0). Please select another point.")
                return
            end_point = (y, x)
            cv2.circle(img_display, (x, y), 3, (0, 0, 255), -1)
            cv2.imshow("Image", img_display)
            
        if start_point and end_point:
            find_path()

def find_path():
    global img_binary, start_point, end_point, img_display
    path = a_star(img_binary, start_point, end_point)
    if path:
        for y, x in path:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= y + i < img_binary.shape[0] and 0 <= x + j < img_binary.shape[1]:
                        if img_binary[y + i, x + j] != 255:
                            continue
                        img_display[y + i, x + j] = [0, 0, 255]
            cv2.imshow("Image", img_display)
            cv2.waitKey(10)  # Delay to visualize the path step-by-step
    else:
        messagebox.showinfo("Error", "No path found! Please select a new end point.")
        end_point = None
        img_display = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2BGR)
        cv2.circle(img_display, (start_point[1], start_point[0]), 3, (0, 255, 0), -1)
        cv2.imshow("Image", img_display)
        cv2.setMouseCallback("Image", on_mouse_click)

def reset_points():
    global start_point, end_point, img_display, img_resized
    start_point = None
    end_point = None
    img_display = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2BGR)
    cv2.imshow("Image", img_display)
    cv2.setMouseCallback("Image", on_mouse_click)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(map_matrix, start, goal):
    # Neighbors include diagonal directions
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
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
img_resized = None
img_display = None
img_binary = None
img_buffered = None
start_point = None
end_point = None

# Create the main window
root = tk.Tk()
root.title("Path Finder")

# Create a frame to hold widgets
frame = tk.Frame(root, padx=50, pady=50)
frame.pack(padx=50, pady=50)

# Create a label for instructions
label = tk.Label(frame, text="Click below to load an image:", font=("Arial", 20))
label.pack(pady=10)

# Create a load button
load_button = tk.Button(frame, text="Load Image", command=load_image, width=20, height=2)
load_button.pack(pady=10)

# Create a reset button
reset_button = tk.Button(frame, text="Reset", command=reset_points, width=20, height=2)
reset_button.pack(pady=10)

# Function to handle closing the main window
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        cv2.destroyAllWindows()
        root.destroy()

# Set the closing event handler
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the tkinter main loop
root.mainloop()

# Close OpenCV windows when the program exits
cv2.destroyAllWindows()
