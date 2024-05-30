#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
import tkinter as tk
import pandas as pd
from tkinter import filedialog, Menu, messagebox
from PIL import Image, ImageTk
from config import BASE_IMG_COORDS, MODIFY_IMG_COORDS, OUTPUT_NAME, OUTPUT_FORMAT, BLACK_PIXEL, OUTPUT_FOLDER
import cv2
import os


class Point:
    def __init__(self, x, y, color, circle_id=None):
        self.x = x
        self.y = y
        self.color = color
        self.circle_id = circle_id

class ImageViewerWindow:
    def __init__(self, root, image_number, main_window):
        self.root = root
        self.image_number = image_number
        self.main_window = main_window
        self.root.title(f"Image Viewer - Image {image_number}")

        self.image1 = None
        self.image2 = None
        # Créer le canevas pour afficher l'image
        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        # Initialiser la liste de points
        self.points = []
        self.cursor_point = None  # Nouvel attribut pour stocker les coordonnées du curseur

        # Créer le menu pour la fenêtre
        menubar = Menu(root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Sauvegarder Points", command=self.save_points, accelerator="Ctrl+S")
        filemenu.add_command(label="Charger Points", command=self.load_points, accelerator="Ctrl+L")
        menubar.add_cascade(label="Fichier", menu=filemenu)
        root.config(menu=menubar)

        # Ouvrir l'image
        self.open_image()

        # Associer la fonction clic à l'événement Button-1 (clic gauche) sur le canevas
        self.canvas.bind("<Button-1>", self.on_click)

        # Associer la fonction pour récupérer les coordonnées en temps réel sous le curseur de la souris
        self.canvas.bind("<Motion>", self.show_pixel_coordinates)

        self.update_zoom()

    def open_image(self):
        # Ouvrir la boîte de dialogue pour choisir un fichier image
        file_path = filedialog.askopenfilename(title=f"Select Image {self.image_number}", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.tif;*.tiff")])

        if self.image_number == 1:
            self.main_window.image(1, file_path)
        elif self.image_number == 2:
            self.main_window.image(2, file_path)

        if file_path:
            # Charger l'image sélectionnée
            self.image = Image.open(file_path)
            self.tk_image = ImageTk.PhotoImage(self.image)

            # Configurer la taille du canevas en fonction de l'image
            self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())

            # Afficher l'image sur le canevas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def on_click(self, event):
        # Déterminer le canevas concerné
        canvas = event.widget

        if canvas == self.canvas:
            points_list = self.points
        else:
            points_list = self.points2  # Supposons que le second canevas soit self.canvas2

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

        # Afficher les coordonnées dans la fenêtre principale
        self.main_window.update_coordinates_label(f"Coordinates: ({x}, {y})")

        # Afficher le zoom dans la fenêtre principale
        zoom_image = self.zoom(x, y)
        self.main_window.show_zoom(zoom_image)

    def update_zoom(self):
        # Mettre à jour l'affichage du zoom
        x_root, y_root = self.root.winfo_pointerx(), self.root.winfo_pointery()  # Obtenir les coordonnées du curseur par rapport à l'écran
        x_canvas = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()  # Convertir les coordonnées du curseur par rapport au canevas principal
        y_canvas = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        #Try catch to avoid ValueError when the mouse is not on the canvas
        try:
            zoom_image = self.zoom(x_canvas, y_canvas)  # Utiliser les coordonnées relatives au canevas pour le zoom
            self.main_window.show_zoom(zoom_image)
        except ValueError:
            pass

        # Programmer la prochaine actualisation
        self.root.after(500, self.update_zoom)

    def zoom(self, x, y, zoom_factor=6):
        # Récupérer la taille du zoom
        zoom_size = 40

        # Déterminer les coordonnées de la zone de zoom dans l'image
        left = max(0, x - zoom_size)
        top = max(0, y - zoom_size)
        right = min(self.image.width, x + zoom_size)
        bottom = min(self.image.height, y + zoom_size)

        # Extraire la zone de zoom de l'image
        zoom_region = self.image.crop((left, top, right, bottom))

        # Redimensionner la zone de zoom
        zoom_region = zoom_region.resize((zoom_region.width * zoom_factor, zoom_region.height * zoom_factor), Image.BOX)

        # Convertir l'image PIL en image Tkinter
        zoom_image = ImageTk.PhotoImage(zoom_region)

        return zoom_image

    def save_points(self):
        # Sauvegarder les points dans un fichier texte
        filename = f"points_image{self.image_number}.txt"
        with open(filename, "w") as file:
            file.write("Type,X,Y\n")
            for i, point in enumerate(self.points, start=1):
                file.write(f"Reference{i},{point.x},{point.y}\n")

    def load_points(self):
        # Déterminer le nom de fichier en fonction du numéro d'image
        if self.image_number == 1:
            filename = "points_image1.txt"
            canvas = self.canvas
            points_list = self.points
        elif self.image_number == 2:
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
                        print(f"Image {self.image_number} - Coordonnées chargées : ({x}, {y}), Couleur : {color}")
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
    
    def show_pixel_coordinates(self, event):
        # Afficher les coordonnées en temps réel sous le curseur de la souris dans la fenêtre principale
        self.main_window.update_coordinates_label(f"Coordinates: ({event.x}, {event.y})")

class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")

        self.im_dst = None
        self.im_src = None

        # Créer le Menu
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Ouvrir Image 1", command=lambda: self.open_image(1), accelerator="Ctrl+O")
        filemenu.add_command(label="Ouvrir Image 2", command=lambda: self.open_image(2), accelerator="Ctrl+Shift+O")
        filemenu.add_command(label="Homographie", command=lambda: self.homography(), accelerator="Ctrl+H")
        filemenu.add_command(label="Homographie de dossier", command=lambda: self.folder_homographie(), accelerator="Ctrl+Shift+H")
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=self.root.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="Fichier", menu=filemenu)
        self.root.config(menu=menubar)

        # Label pour afficher les coordonnées
        self.coordinates_label = tk.Label(root, text="Coordinates: ")
        self.coordinates_label.pack()

        # Label pour afficher le zoom
        self.zoom_label = tk.Label(root)
        self.zoom_label.pack()

    def open_image(self, image_number):
        root = tk.Toplevel(self.root)
        ImageViewerWindow(root, image_number, self)

    def update_coordinates_label(self, text):
        self.coordinates_label.config(text=text)

    def show_zoom(self, image):

        self.zoom_label.config(image=image)
        self.zoom_label.image = image
    
    def image(self, image, path):
        if image==1:
            self.im_dst = cv2.imread(path)
        else:
            self.im_src = cv2.imread(path)

    def next_name(self, folder):
        num = set()
        for fichier in os.listdir(folder):
            nom_fichier, extension = os.path.splitext(fichier)
            try:
                numero = int(nom_fichier)
                num.add(numero)
            except ValueError:
                # Si le fichier n'est pas nommé avec un numéro valide, on l'ignore
                pass
        
        if not num:
            # Si aucun numéro n'existe encore, on retourne 1
            return 1
        else:
            # Sinon, on retourne le prochain numéro inexistant
            return max(num) + 1
    
    def get_measurements(self, fichier_texte):
        """
        Read a file and extract Reference data from findcoords file.

        This function reads the specifie    d file and filters the rows with 'Reference' in the 'Type' column. 
        It then selects the 'X' and 'Y' columns and converts them into a NumPy array.

        Parameters:
            - fichier_texte (str): The path to the file containing the data.

        Returns:
            - numpy.ndarray: A NumPy array containing the 'X' and 'Y' columns of the filtered data.

        Example:
        If the file contains the following data:
        | Type          | X  | Y  |
        |---------------|----|----|
        | Reference     | 1  | 2  |
        | Reference     | 5  | 6  |
        | Measurement   | 3  | 4  |

        Calling get_measurements('data.txt') would return the following NumPy array:
        array([[1, 2],
            [5, 6]])

        Note:
        - Make sure the file exists and has a 'Type' column as well as 'X' and 'Y' columns.
        - The 'Type' column is used to filter rows containing 'Reference'.
        """

        df = pd.read_csv(fichier_texte)
        #DEBUG : #print(df)
        # Filter the rows with 'Measurement' in the 'Type' column
        measurements_df = df[df['Type'].str.startswith('Reference')]

        # Select the X and Y columns, then convert them into a NumPy array
        return measurements_df[['X', 'Y']].to_numpy()

    def homography(self):

        if self.im_dst is None or self.im_src is None:
            messagebox.showerror("Erreur : vous devez ouvrir les deux images avant de faire une homographie !")
            return
        pts_dst = self.get_measurements(BASE_IMG_COORDS)
        pts_src = self.get_measurements(MODIFY_IMG_COORDS)
        # Remove black pixels from images : only pixels not include in the homography will be black (value : 0)
        if BLACK_PIXEL == False:
            self.im_src[self.im_src == 0] = 1
            self.im_dst[self.im_dst == 0] = 1
        else : 
            pass
        # Calculate Homography
        h, status = cv2.findHomography(pts_src, pts_dst)
        #DEBUG : #print (h)
        #DEBUG : #print (status)
        
        #DEBUG : #print(self.im_src.shape[1])
        
        # Warp source image to destination based on homography
        im_out = cv2.warpPerspective(self.im_src, h, (self.im_dst.shape[1], self.im_dst.shape[0]))
        #Save the ouput
        name = self.next_name(OUTPUT_FOLDER)

        cv2.imwrite(OUTPUT_FOLDER+"/"+str(name)+OUTPUT_FORMAT, im_out)
        print("Homographie effectuée !")    
    
    def folder_homographie(self):

        if self.im_src is None:
            messagebox.showerror("Erreur : vous devez ouvrir l'image de repère avant de faire une homographie de dossier !")
            return
        pts_src = self.get_measurements(BASE_IMG_COORDS)
        pts_dst = self.get_measurements(MODIFY_IMG_COORDS)

        h, status = cv2.findHomography(pts_dst, pts_src)

        folder = filedialog.askdirectory(title=f"Select folder")
        for file in (os.listdir(folder)):
            im_dst = cv2.imread(folder + '/' + file)

            # Remove black pixels from images
            if not BLACK_PIXEL:
                self.im_src[self.im_src == 0] = 1
                im_dst[im_dst == 0] = 1

            
            #cv2.imshow("src avant", im_src)
            #cv2.imshow("dst avant", im_dst)
            im_out = cv2.warpPerspective(im_dst, h, (self.im_src.shape[1], self.im_src.shape[0]))
            #cv2.imshow("src apres", im_src)
            #cv2.imshow("dst apres", im_dst)
            #cv2.imshow("Warped Source Image", im_out)
            #cv2.waitKey(0)
            output_filename = '/result_' + file
            cv2.imwrite(OUTPUT_FOLDER + output_filename, im_out)
        print("Homographie du dossier effectuée !")
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()
