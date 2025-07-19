<template>
  <div>
    <!-- Navbar -->
    <nav class="navbar">
      <router-link to="/" class="nav-link">Home</router-link>
      <router-link to="/login" class="nav-link">Login</router-link>
      <router-link to="/register" class="nav-link">Register</router-link>
    </nav>

    <!-- Main Content -->
    <div class="container">
      <h1 class="welcome">WELCOME!</h1>
      <h2 class="subtitle">Household Services Application</h2>
    </div>
  </div>
</template>

<style scoped>
.navbar {
  background-color: green; /* Slightly lighter green */
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Depth effect */
  border-radius: 0; /* Removes any rounded corners */
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 20px;
  margin: 0 15px;
  font-weight: 500;
  transition: background-color 0.3s ease, color 0.3s ease;
  padding: 8px 15px;
  border-radius: 5px; /* Slight rounded corners for button-like feel */
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.2); /* Light highlight effect */
  color: #f1f1f1;
}

.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80vh;
  text-align: center;
}

.welcome {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 20px;
}

.subtitle {
  font-size: 36px;
  margin-bottom: 30px;
}

/* Service image styling (uncomment if you want to add an image) */
.service-image {
  width: 300px;
  height: auto;
}
</style>
