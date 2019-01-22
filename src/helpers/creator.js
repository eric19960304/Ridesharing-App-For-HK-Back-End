
const createUserForFrontend = (data) => {
    let user = {
        email: data.email,
        nickname: data.nickname
    };
    return user;
};

const createNewUserForDatabase = (data) => {
    let user = {
        email: data.email,
        password: data.password,
        nickname: data.nickname,
        avatorSource: data.avatorSource,
    };
    return user;
};

module.exports = {
    createUserForFrontend,
    createNewUserForDatabase
};