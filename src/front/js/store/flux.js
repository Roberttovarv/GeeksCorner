const getState = ({ getStore, getActions, setStore }) => {
    return {
        store: {
            token: null,
            admin: false,
            user: null,
            currentItem: {},
            isLogin: false,
            games: [],
            posts: [],
        },
        actions: {

            login: async (email, password) => {

                const url = process.env.BACKEND_URL + '/api/login';

                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ email, password })
                });

                if (!response.ok) {
                    console.log("Error logging in", response.status, response.statusText);
                    return null;
                }

                const data = await response.json();
                if (data.access_token) {
                    setStore({ token: data.access_token });
                    localStorage.setItem('token', data.access_token);
                    getActions().setIsLogin(true);

                    setStore({ admin: data.is_admin });
                    localStorage.setItem('admin', data.is_admin);
                }
                getActions().fetchProfile()
                return data;
            },

            logout: () => {
                setStore({ token: null });
                localStorage.removeItem('token');
                getActions().setIsLogin(false);
            },

            fetchProfile: async () => {
                const token = getStore().token || localStorage.getItem('token');
                if (!token) {
                    console.log("No token found in localStorage");
                    return;
                }

                const response = await fetch(`${process.env.BACKEND_URL}/api/profile`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    setStore({ user: data.results });
                } else {
                    console.log("Failed to fetch profile");
                }
            },

            setCurrentItem: (item) => {
                setStore({ currentItem: item });
                getActions().fetchProfile()
                getActions().getGames()
            },

            setIsLogin: (login) => {
                setStore({ isLogin: login });
            },

            setUser: (user) => {
                setStore({ user });
            },

            setCurrentUser: (user) => {
                setStore({ user });
            },
            
            getGames: async () => {
                const token = getStore().token
                const host = `${process.env.BACKEND_URL}`;
                const uri = host + '/api/games';
                const options = {
                    method: 'GET',
                    headers: {}
                };
                
                if (token) {
                    options.headers["Authorization"] = `Bearer ${token}`;
                }

                const response = await fetch(uri, options);

                if (!response.ok) {
                    console.log("Error", response.status, response.statusText);
                    return;
                }
                const data = await response.json();

                setStore({ games: data.results });
            },

            addGameLike: async (itemId) => {
                const store = getStore();
                const token = store.token
                const data = {
                    user_id: store.user.id,
                    game_id: itemId
                };

                const uri = `${process.env.BACKEND_URL}/api/like`;
                const options = {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(data),
                };

                const response = await fetch(uri, options);

                if (!response.ok) {
                    console.log("Error", response.status, response.statusText);
                    return;
                }

                const result = await response.json();

                console.log("Like añadido", result, getStore().games);

                await getActions().getGames();
                await getActions().fetchProfile();
            },

            deleteGameLike: async (itemId) => {

                const token = getStore().token;
                const uri = `${process.env.BACKEND_URL}/api/like`;

                const options = {
                    method: "DELETE",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ game_id: itemId })
                };

                const response = await fetch(uri, options);

                if (!response.ok) {
                    console.log("Error", response.status, response.statusText);
                    return;

                }

                console.log("Like eliminado")
                await getActions().getGames();
                await getActions().fetchProfile();
            },

            likedGameId: () => {
                const user = getStore().user

                if (user && user.likes && user.likes.liked_games) {
                    return user.likes.liked_games.map(game => game.id);
                }
                return [];
            },

            handleGameLike: async (gameId) => {

                if (getActions().likedGameId().includes(gameId)) {

                    await getActions().deleteGameLike(gameId);
                }
                else {
                    await getActions().addGameLike(gameId);
                }
                await getActions().getGames();
            },

            getPosts: async () => {
                const token = getStore().token || localStorage.getItem('token'); // Asegúrate de que el token esté disponible
                const host = `${process.env.BACKEND_URL}`;
                const uri = host + '/api/posts';
                const options = {
                    method: 'GET',
                    headers: {}
                };
            
                if (token) {
                    options.headers["Authorization"] = `Bearer ${token}`;
                } else {
                    console.log("No token available for getPosts");
                }
            
                try {
                    const response = await fetch(uri, options);
            
                    if (!response.ok) {
                        console.log("Error in getPosts:", response.status, response.statusText);
                        return;
                    }
            
                    const data = await response.json();
                    setStore({ posts: data.results });
                } catch (error) {
                    console.error("Fetch error in getPosts:", error);
                }
            },

            addPostLike: async (itemId) => {
              
                const token = getStore().token
                const data = {
                    user_id: getStore().user.id,
                    post_id: itemId
                };

                const uri = `${process.env.BACKEND_URL}/api/like`;
                const options = {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(data),
                };

                const response = await fetch(uri, options);

                if (!response.ok) {
                    console.log("Error", response.status, response.statusText);
                    return;
                }

                const result = await response.json();

                console.log("Like añadido", result, getStore().posts);

                await getActions().getPosts();
                await getActions().fetchProfile();
            },

            deletePostLike: async (itemId) => {

                const token = getStore().token;
                const uri = `${process.env.BACKEND_URL}/api/like`;

                const options = {
                    method: "DELETE",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ post_id: itemId })
                };

                const response = await fetch(uri, options);

                if (!response.ok) {
                    console.log("Error", response.status, response.statusText);
                    return;

                }

                console.log("Like eliminado")
                await getActions().getPosts();
                await getActions().fetchProfile();
            },

            likedPostId: () => {
                const user = getStore().user

                if (user && user.likes && user.likes.liked_posts) {
                    return user.likes.liked_posts.map(post => post.id);
                }
                return [];
            },

            handlePostLike: async (postId) => {

                if (getActions().likedPostId().includes(postId)) {

                    await getActions().deletePostLike(postId);
                }
                else {
                    await getActions().addPostLike(postId);
                }
                await getActions().getPosts();
            },
        },
    };
};
export default getState;