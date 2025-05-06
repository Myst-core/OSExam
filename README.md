# OSExam

## What is this?

This is a project for my OS exam that I have researched, designed and created personally.

The website is for a ficticious green energy company called Rolsa Technologies. They specialise in green energy products such as Solar panels, EV chargers, and Home EMS's. 

The brief I was given explained that the website **must**:
- provide customers with information about:
    - green energy products currently available on the market
    - how to reduce their carbon footprint
- allow customers to:
    - schedule consultations & installations
    - calculate their carbon footprint

The brief also gave features they would **like**:
- account registration to allow the users to manage their consultations and data
- accessibility features to support anyone that comes to their website
- a tool to calculate and track energy usage


## How to run

1. Download the ZIP file of the code and unzip the file

2. Open the now unzipped code in a code editor, I use Visual Studio Code and it is what i will be referencing for the rest of this tutorial.

3. Next, you will need to create a virtual environment. You will need Python installed to do this. You can follow [this](https://code.visualstudio.com/docs/python/environments#_creating-environments) tutorial by the official docs of Visual Studio Code. You will need to create a Venv environment.

4. Next, you will need to install the correct packages. In the terminal, using Git Bash, type:
    > pip install flask

    > pip install flask_login

    > pip install flask_bcrypt

5. After everything is installed, go onto app.py and run the file (The triangle in the top right)

6. A message should popup with a url, copy this url and paste it into a browser.

7. The website should be running.