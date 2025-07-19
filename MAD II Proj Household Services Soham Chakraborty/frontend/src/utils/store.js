
import { createStore } from 'vuex';

const store = createStore({
  state() {
    return {
      auth_token: null,
      role: null,
      loggedIn: false,
      user_id: null,
      session_id: null, // Store session ID in Vuex
    };
  },
  mutations: {
    setUser(state) {
      try {
        const user = JSON.parse(localStorage.getItem("user"));
        const newSessionId = user ? `${user.token}-${user.id}` : null;
        const storedSessionId = localStorage.getItem("session_id");

        if (user && user.token) {
          // If there's an active session and it's different, prevent login
          if (storedSessionId) {
            console.warn("User already logged in elsewhere. Preventing login.");
            return; // Prevent login without clearing the session
          }

          // Store new session details
          localStorage.setItem("session_id", newSessionId);
          state.session_id = newSessionId;
          state.auth_token = user.token;
          state.role = user.role;
          state.loggedIn = true;
          state.user_id = user.id;
        }
      } catch (error) {
        console.warn("No valid session found:", error);
      }
    
  },
  logout(state) {
    localStorage.removeItem("user");
    localStorage.removeItem("session_id");
    state.auth_token = null;
    state.role = null;
    state.loggedIn = false;
    state.user_id = null;
    state.session_id = null;
    
  },
},
  getters: {
    isAuthenticated: (state) => !!state.loggedIn && !!state.auth_token,
  },
});

export default store;
