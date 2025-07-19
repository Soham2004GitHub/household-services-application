<template>
  <nav class="navbar">
      <router-link to="/" class="nav-link">Home</router-link>
      <router-link to="/login" class="nav-link">Login</router-link>
      <router-link to="/register" class="nav-link">Register</router-link>
  </nav>
  <div class="container">
    <div class="card mt-5 p-4">
      <h2 class="text-center">Register</h2>
      <form @submit.prevent="submitRegister">
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" class="form-control" type="email" v-model="email" placeholder="Enter email" required />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input id="password" class="form-control" type="password" v-model="password" placeholder="Enter password" required />
        </div>

        <div class="form-group">
          <label for="role">Select Role</label>
          <select id="role" v-model="role" class="form-control" required>
            <option disabled value="">Select Role</option>
            <option value="customer">Customer</option>
            <option value="professional">Professional</option>
          </select>
        </div>

        <!-- Customer Fields -->
        <div v-if="role === 'customer'" class="customer-fields">
          <div class="form-group">
            <label for="name">Name</label>
            <input id="name" class="form-control" v-model="customer.name" placeholder="Enter your name" required />
          </div>

          <div class="form-group">
            <label for="address">Address</label>
            <input id="address" class="form-control" v-model="customer.address" placeholder="Enter your address" required />
          </div>

          <div class="form-group">
            <label for="pincode">Pincode</label>
            <input id="pincode" class="form-control" v-model="customer.pincode" placeholder="Enter your pincode" required />
          </div>

          <div class="form-group">
            <label for="profile_pic">Profile Picture</label>
            <input id="profile_pic" type="file" class="form-control" @change="handleFileUpload('profile_pic', $event)" />
          </div>
        </div>

        <!-- Professional Fields -->
        <div v-if="role === 'professional'" class="professional-fields">
          <div class="form-group">
            <label for="name">Name</label>
            <input id="name" class="form-control" v-model="professional.name" placeholder="Enter your name" required />
          </div>

          <div class="form-group">
            <label for="address">Address</label>
            <input id="address" class="form-control" v-model="professional.address" placeholder="Enter your address" required />
          </div>

          <div class="form-group">
            <label for="pincode">Pincode</label>
            <input id="pincode" class="form-control" v-model="professional.pincode" placeholder="Enter your pincode" required />
          </div>

          <div class="form-group">
            <label for="description">Description</label>
            <textarea id="description" class="form-control" v-model="professional.description" placeholder="Describe your services" required></textarea>
          </div>

          <div class="form-group">
            <label for="service_type">Service Type</label>
            <select id="service_type" v-model="professional.service_type" class="form-control" required>
              <option disabled value="">Select Service Type</option>
              <option v-for="service in services" :value="service.name" :key="service.name">
                {{ service.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="experience">Experience (years)</label>
            <input id="experience" class="form-control" type="number" v-model="professional.experience" placeholder="Enter your experience" required />
          </div>


          <div class="form-group">
            <label for="profile_pic">Profile Picture</label>
            <input id="profile_pic" type="file" class="form-control" @change="handleFileUpload('profile_pic', $event)" />
          </div>

          <div class="form-group">
            <label for="resume">Resume</label>
            <input id="resume" type="file" class="form-control" @change="handleFileUpload('resume', $event)" />
          </div>
        </div>

        <div class="form-group text-center mt-3">
          <button type="submit" class="btn btn-primary">Register</button>
        </div>
      </form>

      <!-- Success and Error Messages -->
      <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
        {{ errorMessage }}
      </div>
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
      role: "",
      services: [],
      successMessage: null,
      errorMessage: null,
      customer: { name: "", address: "", pincode: "", profile_pic: null },
      professional: { name: "", address: "", pincode: "", description: "", service_type: "", experience: null, fee: null, profile_pic: null, resume: null },
    };
  },
  methods: {
    async fetchServices() {
      try {
        const res = await fetch(`${ BASE_URL }/services`);
        if (res.ok) {
          this.services = await res.json();
        }
      } catch (error) {
        console.error("Error fetching services:", error);
      }
    },
    handleFileUpload(field, event) {
      const file = event.target.files[0];
      if (this.role === "customer") {
        this.customer[field] = file;
      } else if (this.role === "professional") {
        this.professional[field] = file;
      }
    },
    async submitRegister() {
      const formData = new FormData();
      formData.append("email", this.email);
      formData.append("password", this.password);
      formData.append("role", this.role);

      if (this.role === "customer") {
        formData.append("name", this.customer.name);
        formData.append("address", this.customer.address);
        formData.append("pincode", this.customer.pincode);
        if (this.customer.profile_pic) {
          formData.append("profile_pic", this.customer.profile_pic);
        }
      } else if (this.role === "professional") {
        formData.append("name", this.professional.name);
        formData.append("address", this.professional.address);
        formData.append("pincode", this.professional.pincode);
        formData.append("description", this.professional.description);
        formData.append("service_type", this.professional.service_type);
        formData.append("experience", this.professional.experience);
        if (this.professional.profile_pic) {
          formData.append("profile_pic", this.professional.profile_pic);
        }
        if (this.professional.resume) {
          formData.append("resume", this.professional.resume);
        }
      }

      try {
        const res = await fetch(`${ BASE_URL }/register`, { method: "POST", body: formData });
        if (res.ok) {
          if (this.role === "professional") {
            this.successMessage = "Registration successful. Wait for Admin Verification.";
          } else {
            this.successMessage = "Registration successful.";
          }
        } else {
          const err = await res.json();
          this.errorMessage = err.message;
        }
      } catch (error) {
        this.errorMessage = "Error during registration. Try again later.";
      }
    },
  },
  created() {
    this.fetchServices();
  },
};
</script>

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
  max-width: 600px;
  margin: auto;
  padding-top: 50px;
}

.card {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background-color: #ffffff;
  padding: 20px;
}

.form-group label {
  font-weight: bold;
}

.form-control {
  border-radius: 5px;
}

button {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  background-color: green; /* Match navbar color */
  color: white;
  border: none;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #45a049; /* Slightly darker green on hover */
}

.alert {
  margin-top: 20px;
}

.customer-fields, .professional-fields {
  margin-top: 20px;
}
</style>
