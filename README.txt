#Item-Catalog

a Menu app where users can add, edit, and delete Clubs in the provided Countries.

#Setup and run the project

##Prerequisites

-Python 3
-Vagrant
-VirtualBox

#How to Run ?

Install VirtualBox and Vagrant
Clone this repo
Unzip and place the Catalog folder in your Vagrant directory
Launch Vagrant
$ Vagrant up 
Login to Vagrant
$ Vagrant ssh
Change directory to /vagrant
$ Cd /vagrant
Initialize the database
$ Python dbconfig.py
Populate the database with some initial data
$ Python additems.py
Launch application
$ Python catalog.py
Open the browser and go to http://localhost:8000

#JSON endpoints

Returns JSON of all countries with their clubs
/catalog.json


