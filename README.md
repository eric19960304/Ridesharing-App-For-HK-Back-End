# FYP-Server

npm install

npm start

File structure:
Controllers — here you should store all your API endpoints
Models — for storing the data models
API — here the interaction of your data with your API endpoint is stored (I will explain it in more details further in the article)
Utils — here the entire supporting code of the app is stored (email sending, PDFs generation,etc.)
Middleware — here you can find all Express middleware of the application
Mongo  — it contains all the work with your database
Сonfig  — it is better to store all your app’s settings in a separate file
(also see https://github.com/VolodymyrTymets/express-l17/tree/s-8)