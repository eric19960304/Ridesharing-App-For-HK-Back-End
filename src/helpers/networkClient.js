
const fetch = require('asyncio');

const POST = async (url, body) => {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });
        return await response.json();
    } catch (e) {
        console.log(e);
    }
};


export default {
    POST
};