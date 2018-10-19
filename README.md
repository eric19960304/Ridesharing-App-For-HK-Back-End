# FYP-Server


prerequisite:

nodejs version 10.x.x installed

clean mongodb running on localhost:27017 [Windows](https://stackoverflow.com/questions/20796714/how-do-i-start-mongo-db-from-windows) [Mac](https://stackoverflow.com/questions/18452023/installing-and-running-mongodb-on-osx)

To start run the server:

`npm install`

`npm start`


Project structure:

controllers: 

    all routes (Restful APIs)

models: 

    mongodb model defined

helpers: 

    utility function / class / constants


middleware: 

    for middleware of express.js


db: 

    database client

config.js: 

    server setting (e.g. secret key location, database url)