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