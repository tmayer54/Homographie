#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, Menu
from PIL import Image, ImageTk

class Point:    
    def __init__(self, x, y, color, circle_id=None):
        self.x = x
        self.y = y
        self.color = color
        self.circle_id = circle_id

class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")

        # Création du Menu
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Ouvrir Image 1", command=lambda: self.open_image(1), accelerator="Ctrl+O")
        filemenu.add_command(label="Enregistrer Points Image 1", command=lambda: self.save_points(1), accelerator="Ctrl+S")
        filemenu.add_command(label="Charger Points Image 1", command=lambda: self.load_points(1), accelerator="Ctrl+P")
        filemenu.add_separator()
        filemenu.add_command(label="Ouvrir Image 2", command=lambda: self.open_image(2), accelerator="Ctrl+Shift+O")
        filemenu.add_command(label="Enregistrer Points Image 2", command=lambda: self.save_points(2), accelerator="Ctrl+Shift+S")
        filemenu.add_command(label="Charger Points Image 2", command=lambda: self.load_points(2), accelerator="Ctrl+Shift+P")
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=self.root.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="Fichier", menu=filemenu)

        self.root.config(menu=menubar)

        # Initialiser les cadres pour les deux images
        self.frame1 = tk.Frame(root)
        self.frame1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.frame2 = tk.Frame(root)
        self.frame2.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Initialiser les canevas pour afficher les images
        self.canvas1 = tk.Canvas(self.frame1)
        self.canvas1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas2 = tk.Canvas(self.frame2)
        self.canvas2.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Initialiser les listes de points pour chaque image
        self.points1 = []
        self.points2 = []

        # Associer la fonction clic à l'événement Button-1 (clic gauche) sur chaque canevas
        self.canvas1.bind("<Button-1>", lambda event: self.on_click(event, 1))
        self.canvas2.bind("<Button-1>", lambda event: self.on_click(event, 2))

    def open_image(self, image_number):
        # Ouvrir la boîte de dialogue pour choisir un fichier image
        file_path = filedialog.askopenfilename(title=f"Select Image {image_number}", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.tif;*.tiff")])

        if file_path:
            # Charger l'image sélectionnée
            image = Image.open(file_path)
            tk_image = ImageTk.PhotoImage(image)

            # Configurer le canevas en fonction de l'image
            if image_number == 1:
                self.canvas1.config(width=tk_image.width(), height=tk_image.height())
                self.canvas1.create_image(0, 0, anchor=tk.NW, image=tk_image)
                self.canvas1.image = tk_image
                self.draw_border(self.canvas1, 0, 0, tk_image.width(), tk_image.height())
            elif image_number == 2:
                self.canvas2.config(width=tk_image.width(), height=tk_image.height())
                self.canvas2.create_image(0, 0, anchor=tk.NW, image=tk_image)
                self.canvas2.image = tk_image
                self.draw_border(self.canvas2, 0, 0, tk_image.width(), tk_image.height())

    def draw_border(self, canvas, x1, y1, x2, y2):
        border_color = "black"  # Couleur de la bordure
        border_width = 2  # Largeur de la bordure
        canvas.create_rectangle(x1 - border_width, y1 - border_width, x2 + border_width, y2 + border_width, outline=border_color, width=border_width)
    
    def load_points(self, image_number):
        # Déterminer le nom de fichier en fonction du numéro d'image
        if image_number == 1:
            filename = "points_image1.txt"
            canvas = self.canvas1
            points_list = self.points1
        elif image_number == 2:
            filename = "points_image2.txt"
            canvas = self.canvas2
            points_list = self.points2

        try:
            with open(filename, "r") as file:
                # Supprimer les points existants
                for point in points_list:
                    canvas.delete(point.circle_id)
                points_list.clear()

                # Lire les points à partir du fichier
                for i, line in enumerate(file):
                    if i == 0:  # Passer la première ligne
                        continue

                    parts = line.strip().split(',')
                    if len(parts) >= 3:  # Vérifier que la ligne contient suffisamment de parties
                        x, y = int(parts[1]), int(parts[2])
                        color = self.get_next_color(points_list)  # Utiliser la prochaine couleur disponible
                        point = Point(x, y, color)
                        circle_id = canvas.create_oval(x - 5, y - 5, x + 5, y + 5, outline=color, width=2)
                        point.circle_id = circle_id
                        points_list.append(point)

                        # Afficher les coordonnées dans le terminal
                        print(f"Image {image_number} - Coordonnées chargées : ({x}, {y}), Couleur : {color}")
                    else:
                        print(f"Ignorer la ligne mal formatée dans {filename}: {line.strip()}")
        except FileNotFoundError:
            print(f"Le fichier {filename} n'existe pas.")

    def get_next_color(self, points_list):
        # Définir une liste de couleurs disponibles
        available_colors = ['red', 'blue', 'green', 'purple', 'orange', 'yellow']
        # Trouver la prochaine couleur disponible qui n'est pas déjà utilisée
        for color in available_colors:
            if all(point.color != color for point in points_list):
                return color
        # Si toutes les couleurs sont déjà utilisées, utiliser une couleur par défaut (noir)
        return 'black'

    def on_click(self, event, image_number):
        # Déterminer le canevas concerné
        if image_number == 1:
            canvas = self.canvas1
            points_list = self.points1
        elif image_number == 2:
            canvas = self.canvas2
            points_list = self.points2

        # Vérifier si le clic est à proximité d'un cercle existant
        for point in points_list:
            distance = ((event.x - point.x)**2 + (event.y - point.y)**2)**0.5
            if distance <= 5:  # Distance seuil pour considérer que le clic est proche d'un cercle existant
                # Supprimer le cercle du canevas
                canvas.delete(point.circle_id)
                # Supprimer le point de la liste des points
                points_list.remove(point)
                return

        # Limiter le nombre de points à 6 par image
        if len(points_list) >= 6:
            return

        # Obtenir les coordonnées du clic sur le canevas
        x, y = event.x, event.y

        # Définir une couleur différente pour chaque point (jusqu'à 5 points) 
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'yellow']
        color = colors[len(points_list)]

        # Ajouter le point à la liste
        point = Point(x, y, color)
        points_list.append(point)

        # Afficher le cercle sur le canevas
        circle_id = canvas.create_oval(x-5, y-5, x+5, y+5, outline=color, width=2)

        # Mettre à jour l'ID du cercle dans l'objet Point
        point.circle_id = circle_id

        # Afficher les coordonnées dans le terminal
        print(f"Image {image_number} - Point {len(points_list)} - Coordonnées : ({x}, {y}), Couleur : {color}")

    def save_points(self, image_number):
        # Déterminer la liste de points et le nom de fichier en fonction du numéro d'image
        if image_number == 1:
            points_list = self.points1
            filename = "points_image1.txt"
        elif image_number == 2:
            points_list = self.points2
            filename = "points_image2.txt"

        # Sauvegarder les points dans un fichier texte
        with open(filename, "w") as file:
            # Write the header
            file.write("Type,X,Y\n")
            
            # Write the coordinates of each point
            for i, point in enumerate(points_list, start=1):
                file.write(f"Reference{i},{point.x},{point.y}\n")
                print(f"Points saved to {filename}: Reference{i}, {point.x}, {point.y}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()
