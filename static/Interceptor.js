function refreshToken() {
    return new Promise((resolve, reject) => {
        const refresh_token = localStorage.getItem('refresh_token');
        axios.post('/api/token/refresh', {}, {
            headers: { 'Authorization': 'Bearer ' + refresh_token }
        }).then(response => {
            if (response.data.access_token) {
                localStorage.setItem('access_token', response.data.access_token);
                localStorage.setItem('refresh_token', response.data.refresh_token);
                resolve(response.data.access_token);
            } else {
                reject('Failed to refresh token');
            }
        }).catch(error => {
            console.error('Error:', error);
            window.location.href = '/'; // Redirect to login page
        });
    });
}


//Axios interceptor to attach the JWT to every request
console.log("Setting up interceptors...");
axios.interceptors.request.use(function (config) {
    const token = localStorage.getItem('access_token');
    console.log("Interceptor triggered with token:", token);
    if (token) {
        config.headers.Authorization = 'Bearer ' + token;
    }
    return config;
}, function (error) {
    return Promise.reject(error);
});

axios.interceptors.response.use(response => response, error => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        return refreshToken().then(newToken => {
            originalRequest.headers.Authorization = 'Bearer ' + newToken;
            return axios(originalRequest);
        });
    }
    return Promise.reject(error);
});