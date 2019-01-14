const authRouter = require('./auth');
const testRouter = require('./test');
const apiRouter = require('./api');
const notifyMatchResultRouter = require('./notifyMatchResult');

module.exports = {
    authRouter,
    testRouter,
    apiRouter,
    notifyMatchResultRouter
};