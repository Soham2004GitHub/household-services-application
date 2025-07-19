import { createRouter, createWebHistory } from 'vue-router'
import store from '../utils/store.js' // Ensure correct store path

import LoginPage from '../pages/LoginPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import AdminDashboard from '../pages/AdminDashboard.vue'
import CustomerDashboard from '../pages/CustomerDashboard.vue'
import ProfessionalDashboard from '../pages/ProfessionalDashboard.vue'
import CreateService from '../pages/CreateService.vue'
import ViewServices from '../pages/ViewServices.vue'
import AdminStats from '../pages/AdminStats.vue'
import Home from '../pages/Homepage.vue';
/*
const Home = {
    template: `<h1> Welcome to Household Services! </h1>`,
}
*/
const routes = [
    { path: '/', component: Home },
    { path: '/login', component: LoginPage },
    { path: '/register', component: RegisterPage },
    { 
        path: '/admindashboard/usersview', 
        component: AdminDashboard, 
        meta: { requiresLogin: true, role: "admin" }, 
    },
    { 
        path: '/customerdashboard/:customer_id', 
        component: CustomerDashboard, 
        meta: { requiresLogin: true, role: "customer" }, 
    },
    { 
        path: '/professionaldashboard/:professional_id', 
        component: ProfessionalDashboard, 
        meta: { requiresLogin: true, role: "professional" }, 
    },
    { 
        path: '/createservice', 
        component: CreateService,
    },
    {
        path: '/admindashboard/servicesview', 
        component: ViewServices,
    },
    {
        path: '/admindashboard/statistics', 
        component: AdminStats,
    },
]

// ✅ Use Vue 3 Router Syntax
const router = createRouter({
    history: createWebHistory(),
    routes,
})

// ✅ Correct Vue Router Navigation Guard for Vue 3
router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresLogin)) {
        if (!store.state.loggedIn) {
            next('/login') // Redirect to login if not logged in
        } else if (to.meta.role && to.meta.role !== store.state.role) {
            alert('Role not authorized')
            next('/') // Redirect to home if role is not authorized
        } else {
            next() // Proceed
        }
    } else {
        next() // Allow access if no login required
    }
})

export default router
