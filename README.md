# HKUCS FYP Back End Server for Ridesharing App


Also see the App repository: https://github.com/eric19960304/Ridesharing-App-For-HK

prerequisite:

1. nodejs version 10.x.x installed

2. clean mongodb running on localhost:27017 ( [Windows](https://stackoverflow.com/questions/20796714/how-do-i-start-mongo-db-from-windows) | [Mac](https://stackoverflow.com/questions/18452023/installing-and-running-mongodb-on-osx) )

3. yarn with version >=1.12.3 installed

4. redis running on port 6379 (default port)


Required enviroment variables in server (see config.js):
* MONGODB_PASSWORD
* PROD
* JWT_SECRET
* GMAIL_PASSWORD (for hkucsfyp2018threeriders@gmail.com, you can change the email address in config.js)
* GOOGLE_MAP_API_KEY


For Windows users to install bcrypt (ref: https://stackoverflow.com/questions/41899719/how-to-npm-install-bcrypt-on-windows-7):
* use powershell as admin to run `npm install --global --production windows-build-tools`
* then run the following `npm install node-gyp -g`


To install all the packages (under project's root directory):

`yarn`

To run the server in development mode:

`yarn start`

To run the server in production mode (all env variables should be set):

`yarn run prod`



# Matching Engine

prerequisite:

1. Python >= 3.5.2

2. pip is for above python version command avaliable in your terminal

3. clean mongodb running on localhost:27017 ( [Windows](https://stackoverflow.com/questions/20796714/how-do-i-start-mongo-db-from-windows) | [Mac](https://stackoverflow.com/questions/18452023/installing-and-running-mongodb-on-osx) )

4. redis running on port 6379 (default port)



To install all the packages (under /matchingEngine directory):

`pip install -r requirements.txt`

To run the server "engine_v1" (under /matchingEngine directory):

`python engine_v1.py`
