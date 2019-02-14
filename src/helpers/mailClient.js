const config = require('../../config');
const gmailClient = require('gmail-send');

const defaultMailSetting = {
    ...config.mailConfig,
    to: config.mailConfig.user, // send to itself
    subject: 'default mail subject',
    text:    'default mail content',
};

const mailCallback = (err, res) => {
    console.log('Sending Email, err: ', err, 'response: ', res);
};

const send = (to, subject, html) => {
    gmailClient(defaultMailSetting)(
        {
            to, subject, html  // override mail setting
        },
        mailCallback
    );
};


module.exports = {
    send
};