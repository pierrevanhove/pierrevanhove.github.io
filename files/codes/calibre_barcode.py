# -*- coding: utf-8 -*-
# Author: Pierre Vanhove
# Date: August 9, 2026
# Description: A script for generating barcodes for Calibre library management.
import cv2
import numpy as np
import subprocess
from pyzbar.pyzbar import decode

# Path to the Calibre command-line tool on macOS
CALIBREDB_PATH = "/Applications/calibre.app/Contents/MacOS/calibredb"

# Initialize the webcam
cap = cv2.VideoCapture(0)

scanned_barcodes = set()
books_to_add = []
scanning_active = True

print("Camera starting... Please hold up a barcode.")

while scanning_active:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Decode barcodes in the frame
    decoded_objects = decode(frame)

    for obj in decoded_objects:
        barcode_type = obj.type
        barcode_data = obj.data.decode('utf-8')

        # Draw a rectangle around the barcode (UI formatting)
        points = obj.polygon
        if len(points) > 4:
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.int32))
            cv2.polylines(frame, [hull], True, (0, 255, 0), 2)
        else:
            points = [(point.x, point.y) for point in points]
            for j in range(len(points)):
                cv2.line(frame, points[j], points[(j + 1) % len(points)], (0, 255, 0), 2)

        cv2.putText(frame, barcode_data, (obj.rect.left, obj.rect.top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Process only if we haven't seen this barcode yet
        if barcode_data not in scanned_barcodes:
            print(f"\n--- New Barcode Detected ---")
            print(f"Type: {barcode_type}")
            print(f"Data: {barcode_data}")
            
            # Add to our tracking lists
            scanned_barcodes.add(barcode_data)
            
            # We only want to send EAN13 (ISBN) codes to Calibre
            if barcode_type == 'EAN13':
                books_to_add.append(barcode_data)

            # Write to our backup text file
            with open("scanned_barcodes.txt", "a") as file:
                file.write(f"Type: {barcode_type}, Data: {barcode_data}\n")
            
            # Briefly update the OpenCV window to show the green box before pausing
            cv2.imshow('Barcode Reader', frame)
            cv2.waitKey(1)
            
            # Pause and ask the user in the terminal
            while True:
                user_choice = input("\nIs there another barcode to scan? (yes/no): ").strip().lower()
                if user_choice in ['yes', 'y']:
                    print("Resuming camera... Please present the next barcode.")
                    break # Break the prompt loop, resume camera
                elif user_choice in ['no', 'n']:
                    scanning_active = False
                    break # Break the prompt loop, prepare to exit
                else:
                    print("Please answer 'yes' or 'no'.")
            
            # Break out of the decoded_objects for-loop so we don't process multiple in one frame 
            # while trying to handle the user input
            break 

    # Display the resulting frame (only updates if not paused waiting for input)
    if scanning_active:
        cv2.imshow('Barcode Reader', frame)

    # Break the loop if 'q' is pressed on the video window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Turn off the camera immediately after answering "no"
cap.release()
cv2.destroyAllWindows()


# --- CALIBRE BATCH UPLOAD SECTION ---
if books_to_add:
    print(f"\nCamera closed. Preparing to send {len(books_to_add)} books to Calibre...")
    
    for isbn in books_to_add:
        print(f"Adding ISBN {isbn} to Calibre...")
        try:
            # Run the calibredb command to add an empty book with the ISBN
            subprocess.run([
                CALIBREDB_PATH, 
                "add", 
                "--empty", 
                "--isbn", 
                isbn
            ], check=True)
            print(f"-> Successfully added {isbn}!")
        except FileNotFoundError:
            print(f"-> Error: Could not find Calibre at {CALIBREDB_PATH}.")
            break # Stop trying if Calibre isn't installed
        except subprocess.CalledProcessError as e:
            print(f"-> Error adding {isbn} to Calibre: {e}")
            
    print("\nAll done! You can open Calibre now.")
else:
    print("\nNo ISBNs were scanned. Exiting program.")
