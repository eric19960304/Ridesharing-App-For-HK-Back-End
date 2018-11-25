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

class MailClient {

    constructor(){
        this.sendMailMethod = gmailClient(defaultMailSetting);
    }

    sendTestMail(){
        this.sendMailMethod({}, mailCallback);
    }

    send(to, subject, text){
        this.sendMailMethod(
            {
                to, subject, text  // override mail setting
            },
            mailCallback
        );
    }

}

module.exports = MailClient;