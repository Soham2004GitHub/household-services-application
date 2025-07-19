<template>
  <div>
    <!-- Navbar -->
    <nav class="navbar">
      <router-link to="/" class="nav-link">Home</router-link>
      <router-link to="/login" class="nav-link">Login</router-link>
      <router-link to="/register" class="nav-link">Register</router-link>
    </nav>

    <!-- Login Form -->
    <div class="login-container">
      <div class="form-group">
        <input
          type="email"
          class="form-control"
          placeholder="Email"
          v-model="email"
        />
      </div>
      <div class="form-group">
        <input
          type="password"
          class="form-control"
          placeholder="Password"
          v-model="password"
        />
      </div>
      <button class="btn w-100" @click="submitLogin">Login</button>

      <!-- Error Message in Red Color -->
      <p v-if="errorMessage" class="custom-error-message">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import { BASE_URL } from "../base.js";
export default {
  data() {
    return {
      email: "",
      password: "",
      errorMessage: null, // Ensure it's an empty string, not null
    };
  },
  methods: {
    async submitLogin() {
  this.errorMessage = ""; // Reset error message
  this.$nextTick(() => {
    console.log("Error Message Reset:", this.errorMessage);
  });

  const activeSession = this.$store.state.loggedIn;
  if (activeSession) {
    this.errorMessage = "You are already logged in. Please log out before logging in again.";
    console.log("Error Message Set:", this.errorMessage);
    return;
  }

  try {
    const res = await fetch(`${BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: this.email, password: this.password }),
    });

    if (res.ok) {
      const data = await res.json();
      const existingSession = JSON.parse(localStorage.getItem("user"));

      if (existingSession && existingSession.token && existingSession.id !== data.id) {
        this.errorMessage = "User Logged In. Log Out Previous Session first.";
        console.log("Error Message Set:", this.errorMessage);
        return;
      }

      localStorage.setItem("user", JSON.stringify(data));
      this.$store.commit("setUser");

      if (data.role === "professional" && !data.verified) {
        this.errorMessage = "Wait for Admin Verification.";
        console.log("Error Message Set:", this.errorMessage);
        return;
      }

      if (data.role !== "admin" && data.blocked) {
        this.errorMessage = "Your account is blocked. Contact admin.";
        console.log("Error Message Set:", this.errorMessage);
        return;
      }

      switch (data.role) {
        case "customer":
          this.$router.push(`/customerdashboard/${data.id}`);
          break;
        case "professional":
          this.$router.push(`/professionaldashboard/${data.id}`);
          break;
        case "admin":
          this.$router.push("/admindashboard/usersview");
          break;
        default:
          this.errorMessage = "Unknown role. Please contact support.";
          console.log("Error Message Set:", this.errorMessage);
      }
    } else {
      const err = await res.json();
      this.errorMessage = err.message || "Login failed. Try again.";
      console.log("Error Message Set:", this.errorMessage);
    }
  } catch (error) {
    this.errorMessage = "An error occurred during login. Try again later.";
    console.log("Error Message Set:", this.errorMessage);
  }

  
  },
  },
};
</script>

<style scoped>
.navbar {
  background-color: green;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 20px;
  margin: 0 15px;
  font-weight: 500;
  transition: background-color 0.3s ease, color 0.3s ease;
  padding: 8px 15px;
  border-radius: 5px;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.2);
  color: #f1f1f1;
}

.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.login-container .form-group {
  margin-bottom: 15px;
}

.login-container .form-control {
  border-radius: 5px;
  padding: 12px;
  border: 1px solid #ccc;
  transition: border 0.3s ease;
}

.login-container .form-control:focus {
  border-color: green;
}

.login-container .btn {
  font-size: 16px;
  font-weight: bold;
  background-color: green;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}

.login-container .btn:hover {
  background-color: #45a049;
}

/* Red error message styling */
.custom-error-message {
  color: red !important;
  font-size: 20px !important;
  display: block !important;
  visibility: visible !important;
}
</style>
