const isDriverOnline = (driverLocation) => {
    const currentTime = new Date();
    const driverLastUpdate = driverLocation.timestamp;
    const timeDiff = currentTime.getTime() - driverLastUpdate;
    return Boolean(timeDiff <= 7000.0);
};

module.exports = {
    isDriverOnline
};