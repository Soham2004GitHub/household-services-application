<template>
<nav class="navbar navbar-expand-lg navbar-dark bg-success shadow">
      <div class="container-fluid">
        <div class="collapse navbar-collapse">
          <h1 class="text-center text-white">Admin Dashboard</h1>
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link to="/admindashboard/usersview" class="nav-link">
                <h3 class="text-center">Home</h3>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/createservice" class="nav-link">
                <h3 class="text-center">Create Service</h3>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admindashboard/servicesview" class="nav-link">
                <h3 class="text-center">View Services</h3>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admindashboard/statistics" class="nav-link">
                <h3 class="text-center">View Statistics</h3>
              </router-link>
            </li>
            <li class="nav-item">
              <button class="btn btn-info mx-2 shadow-sm" @click="create_csv">Get Service Requests Data</button>
            </li>
            <li class="nav-item">
              <button class="btn btn-danger mx-2 shadow-sm" @click="logout">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  <div class="container mt-4">
    <h2 class="text-center">Create a New Service</h2>

    <div class="card shadow-sm p-4">
      <form @submit.prevent="createService">
        <div class="mb-3">
          <label class="form-label">Service Name</label>
          <input type="text" class="form-control" v-model="name" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Base Price ($)</label>
          <input type="number" class="form-control" v-model.number="base_price" step="0.01" min="0" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Time Required (minutes)</label>
          <input type="number" class="form-control" v-model.number="time_required" min="1" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Description</label>
          <textarea class="form-control resizable-textarea" v-model="description" required></textarea>
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="!isFormValid">
          Create Service
        </button>

        <!-- Feedback Messages -->
        <div v-if="message" class="alert mt-3" :class="messageType">
          {{ message }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { BASE_URL } from "../base.js";
export default {
  data() {
    return {
      name: "",
      base_price: null,
      time_required: null,
      description: "",
      message: "",
      messageType: "",
    };
  },
  computed: {
    isFormValid() {
      return this.name && this.base_price > 0 && this.time_required > 0 && this.description;
    },
  },
  methods: {
    async createService() {
      try {
        const res = await fetch(`${ BASE_URL }/createservice`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: this.name,
            base_price: this.base_price,
            time_required: this.time_required,
            description: this.description,
          }),
        });

        if (res.ok) {
          this.message = "Service created successfully!";
          this.messageType = "alert-success";
          this.resetForm();
        } else {
          this.message = "Error creating service. Please try again.";
          this.messageType = "alert-danger";
        }
      } catch (error) {
        this.message = "Network error. Please try again.";
        this.messageType = "alert-danger";
      }
    },
    resetForm() {
      this.name = "";
      this.base_price = null;
      this.time_required = null;
      this.description = "";
    },
    logout() {
      this.$store.commit("logout");
      this.$router.push("/login");
    },
  },
};
</script>

<style>
.resizable-textarea {
  min-height: 100px;
}
</style>
