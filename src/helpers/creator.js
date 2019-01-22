
const createUserForFrontend = (data) => {
    let user = {
        email: data.email,
        nickname: data.nickname,
        avatarSource: null
    };
    return user;
};

const createNewUserForDatabase = (data) => {
    let user = {
        email: data.email,
        password: data.password,
        nickname: data.nickname,
        avatarSource: data.avatarSource,
    };
    return user;
};

module.exports = {
    createUserForFrontend,
    createNewUserForDatabase
};