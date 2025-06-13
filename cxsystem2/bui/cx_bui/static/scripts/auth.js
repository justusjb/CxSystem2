var github_auth_response;
var session_token = '';

function authenticate(callback) {
    // Get GitHub token from localStorage (set during OAuth flow)
    session_token = localStorage.getItem('github_token');
    
    if (!session_token) {
        console.warn('No GitHub token found. User needs to authenticate.');
        // Redirect to GitHub OAuth
        redirectToGitHubAuth();
        return;
    }

    // GitHub User API endpoint
    const USER_API = 'https://api.github.com/user';

    $.ajax({
        url: USER_API,
        headers: {
            'Authorization': 'Bearer ' + session_token,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.v3+json'
        },
        method: 'GET',
        success: function (data) {
            github_auth_response = data;
            
            // GitHub returns different field names than HBP
            var displayName = data.name || data.login; // Use full name or username
            var profilePicture = data.avatar_url;
            
            document.getElementById('welcome').innerHTML = "Hello " + displayName + "  <img id=\"imagebox\" width=\"30\" height=\"30\" style='margin-left:5px;'/>";
            document.getElementById('imagebox').src = profilePicture;

            console.log('GitHub user data:', data);
        },
        error: function(xhr, status, error) {
            console.error('GitHub authentication failed:', error);
            
            if (xhr.status === 401) {
                // Token is invalid, clear it and redirect to auth
                localStorage.removeItem('github_token');
                redirectToGitHubAuth();
            }
        }
    });

    if (callback != null) {
        callback();
    }
    
    return Promise.resolve({ access_token: session_token });
}

function redirectToGitHubAuth() {
    var clientId = window.GITHUB_CLIENT_ID || 'YOUR_GITHUB_CLIENT_ID'; // Use from template or fallback
    var redirectUri = encodeURIComponent(window.location.origin + '/callback');
    var state = Math.random().toString(36).substring(7); // Random state for security
    
    var authUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=user:email&state=${state}`;
    
    window.location.href = authUrl;
}

// Function to check if user is authenticated
function isAuthenticated() {
    return localStorage.getItem('github_token') !== null;
}

// Function to logout
function logout() {
    localStorage.removeItem('github_token');
    session_token = '';
    github_auth_response = null;
    
    // Redirect to home or show login button
    window.location.reload();
}
