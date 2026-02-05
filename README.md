# encryption
Here are files that encrypts txt file into png image.
Script stego_lsb.py encrypts a file inside png image (default image is given in folder, feel free to use any other PNG image)
For running script you will need python installed on your machine.
Also you will need Pillow lib installed. If you don't have it, run command in python: pip install pillow numpy.

For running script in encryption mode open command prompt, navigate to folder with script, image and file you want to encrypt.
Run a command: python stego_lsb2.py hide default.png encrtypted.txt nothing_here.png
This command takes file "encrypted.txt" and image "default.png" and generates new image "nothing_here.png" similar to "default.png" just with file inside it.

For running script in decryption mode open command prompt, navigate to folder with script and image with encrypted file you want to extract.
Run a command: python stego_lsb2.py extract nothing_here.png
This command will extract txt file from image and put it inside "extracted_encrtypted.txt"

As of now, script runs only on PNG images and TXT files.
