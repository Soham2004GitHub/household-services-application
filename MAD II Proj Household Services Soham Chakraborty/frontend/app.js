import { createApp } from 'vue';
import Navbar from './src/components/navbar.js';
import router from './src/utils/router.js';
import store from './src/utils/store.js';
import './src/background.css'; // Import global styles

const app = createApp({
    template: `
        <div class="app-container"> 
            <router-view></router-view>
        </div>
    `,
    components: { Navbar }
});

app.use(router);
app.use(store);
app.mount('#app');