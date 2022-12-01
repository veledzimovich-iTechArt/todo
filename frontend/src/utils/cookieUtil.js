
export function getCookies(document) {
    let result = {};
    document.cookie.split(';').forEach(cookie => {
        let array = cookie.split('=')
        if (array.length > 1) {
            result[array[0].trim()] = array[1].trim()
        }
    });
    return result
};

export function setCookie(
    document, key, value, days = 1, hours = 24, minutes = 60, sec = 60
) {
    const d = new Date();
    d.setTime(d.getTime() + (days * hours * minutes * sec * 1000));
    let expires = "Expires=" + d.toUTCString();
    document.cookie = `${key}=${value}; ${expires};`;
};

export function removeCookie(document, key) {
    document.cookie = `${key}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
};
