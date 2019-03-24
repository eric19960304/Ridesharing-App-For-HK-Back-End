const haversineDistance = (location1, location2) => {
    // in km
    const toRad = (x) => {
        return x * Math.PI / 180;
    };
  
    const lat1 = location1.latitude;
    const lat2 = location2.latitude;
  
    const dLat = toRad(location1.latitude - location2.latitude);
    const dLong = toRad( location1.longitude - location2.longitude);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
            Math.sin(dLong / 2) * Math.sin(dLong / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = 6371 * c;
  
    return distance;
};


module.exports = {
    haversineDistance
};