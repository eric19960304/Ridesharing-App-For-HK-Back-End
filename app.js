const express = require('express');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const http = require('http');
const https = require('https');

const { authRouter, testRouter, apiRouter} = require('./src/controllers');
const { verifyJwt } = require('./src/middlewares/auth');
const config = require('./config');

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(bodyParser.json());
app.set('view engine', 'pug');
app.set('views', './src/views');


// db
const MongoClient = require('./src/db/mongoClient');
const mongoClient = new MongoClient(config);
mongoClient.connect();

// static files
app.use(express.static('public'));

// print request for all routes
const printRequest = (req, res, next) => { console.log(req.body); next(); };
app.use(printRequest);

/*
All routes:
/auth/login [POST]
/auth/signup [POST]
/auth/reset-password/request [POST]
/auth/reset-password/:token [GET]
/auth/reset-password/:token [POST]
/api/secret/google-map-api-key [POST]
/api/driver/location-update [POST]
/api/user/edit-profile [POST]
*/
app.use('/auth', authRouter);
app.use(
    '/api', 
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    apiRouter
);
app.use(
    '/test', 
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    testRouter
);

console.log('using config:', config);

const httpServer = http.createServer(app);

if(process.env.PROD){
    console.log('production mode');

    httpServer.listen(80, () => {
        console.log('Server is running on Port 80');
    });

    const fs = require('fs');
    const privateKey  = fs.readFileSync('/ssl_cert/server.key', 'utf8');
    const certificate = fs.readFileSync('/ssl_cert/server.crt', 'utf8');
    const ca = fs.readFileSync('/ssl_cert/ca.crt', 'utf8');
    const credentials = {
        key: privateKey, 
        cert: certificate,
        ca
    };
    const httpsServer = https.createServer(credentials, app);
    httpsServer.listen(443, () => {
        console.log('Server is running on Port 443');
    });
}else{
    console.log('development mode');
    
    httpServer.listen(80, () => {
        console.log('Server is running on Port 80');
    });
}

// const websocket = require('socket.io')(httpServer);
// const { Message } = require('./src/models');

// users = {}

// websocket.on('connection', (socket) => {
//     console.log('A client just joined on', socket.id);
//     socket.on('userJoined', (message) => onUserJoined(message, socket));
//     socket.on('message', (message) => onMessageReceived(message, socket));
// });

// const onUserJoined = (message, socket) => {
//     console.log(message);
//     user = message.text
//     if (!(user in users)) {
//         sendExistingMessages(user, socket);
//     } else {
//       users[user] = socket.id;
//       sendExistingMessages(user, socket);
//     }
//     // try {
        
//     // } catch(err) {
//     //     console.log(err);
//     // }
// }

// const sendExistingMessages = (user, socket) => {
//     //let receiverId = user;

//     Message.find({ $or: [ { 'senderId': user }, { 'recieverId': user } ]  })
//         .sort({ 'createdAt': -1 })
//         .exec(function (err, message) {
//             if (err){
//                 console.log(err);
//                 return res.status(200).json({
//                     message: 'Something wrong! Please try again latter.'
//                 });
//             }else{
//                 if (!message.length) return;
//                 for(var i = 0; i < message.length; i++){
//                     message[i].user = user;
//                     console.log(message[i]);
//                 }
//             }
//         });
//         // .then((message) => {
//         //     console.log(message);
//         //     console.log(message.toObject());
//         //     var newMessage = message.toObject();
//         //     // If there aren't any messages, then return.
//         //     if (!message.length) return;
//         //     for(var i = 0; i < newMessage.length; i++){
//         //         newMessage[i].user = user;

//         //     }
//         //     console.log(newMessage)
//         //     socket.emit('message', newMessage.reverse());
//         // })
//         // .catch(err => {
//         //     console.log(err);
//         //     return res.status(200).json({
//         //         message: 'Something wrong! Please try again latter.'
//         //     });
//         // });
        
//         // .sort()
//         // .toArray((err, messages) => {
//         //     if (err) console.log(err);
//         //     // If there aren't any messages, then return.
//         //     if (!messages.length) return;
//         //     socket.emit('message', messages.reverse());
//         // });

//         //socket.clients[senderSocket].emit();
// }

// const onMessageReceived = (message, senderSocket) => {
    
//     console.log(message);

//     const newMessage = new Message({
//         senderId: message.user.id,
//         receiverId: 'server',
//         message: message.text,
//         createdAt: message.createdAt
//     });

//     newMessage.save()
//         .catch(err => {
//             console.log('insert message error: ', err);
//             return res.status(200).json({
//                 message: 'Something wrong! Please try again latter.'
//             });
//         });
// }

const socketio = require('socket.io')(httpServer);
const socketRouter = require('./src/controllers/socket/index')(socketio);
app.use('/socket', socketRouter);