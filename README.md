# FYP-Server


prerequisite:

nodejs version 10.x.x installed

clean mongodb running on localhost:27017 ( [Windows](https://stackoverflow.com/questions/20796714/how-do-i-start-mongo-db-from-windows) | [Mac](https://stackoverflow.com/questions/18452023/installing-and-running-mongodb-on-osx) )

Required enviroment variables in server (see config.js):
* MONGODB_PASSWORD
* PROD
* JWT_SECRET
* GMAIL_PASSWORD (for hkucsfyp2018threeriders@gmail.com, you can change the email address in config.js)
* GOOGLE_MAP_API_KEY

To run the server:

`npm install`

`npm start`


Project structure:

controllers

* routes (Restful APIs)

models

* define database models

helpers: 

* utility function / class / constants


middlewares

* reusable middlewares in express.js


db

* database client

config.js

* server setting (e.g. secret key location, database url)
