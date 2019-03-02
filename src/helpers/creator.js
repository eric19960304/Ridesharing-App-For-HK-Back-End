
const createUserForFrontend = (data) => {
    let user = {
        userId: data._id.toString(),
        email: data.email,
        nickname: data.nickname,
        avatarSource: data.avatarSource,
        carplate:data.carplate,
        contact:data.contact,
        isDriver:data.isDriver,
    };
    return user;
};

const createNewUserForDatabase = (data) => {
    let user = {
        email: data.email,
        password: data.password,
        nickname: data.nickname,
        avatarSource: data.avatarSource,
        carplate:data.carplate,
        contact:data.contact,
        isDriver:data.isDriver,
    };
    return user;
};

module.exports = {
    createUserForFrontend,
    createNewUserForDatabase
};