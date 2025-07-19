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
  <div class="container py-5">
    <h2 class="text-center mb-4">Manage Services</h2>

    <!-- Loop through services array using v-for -->
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div class="col" v-for="service in services" :key="service.name">
        <!-- Card in each column with bg-info -->
        <div class="card bg-info text-white">
          <div class="card-body">
            <h5 class="card-title"><strong>Name:</strong> {{ service.name }}</h5>
            <p class="card-text"><strong>Base Price:</strong> ${{ service.base_price }}</p>
            <p class="card-text"><strong>Time Required:</strong> {{ service.time_required }} mins</p>
            <p class="card-text"><strong>Description:</strong> {{ service.description }}</p>
            <button class="btn btn-primary me-2" @click="openEditModal(service)">Edit</button>
            <button class="btn btn-danger" @click="deleteService(service.id)">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal for Editing Service -->
    <div v-if="isEditModalVisible" class="modal-overlay">
      <div class="modal-content">
        <button @click="closeEditModal" class="btn btn-secondary close-btn">Close</button>
        <h3>Edit Service</h3>
        <form @submit.prevent="updateService">
          <div class="mb-3">
            <label class="form-label">Name:</label>
            <input v-model="selectedService.name" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Base Price:</label>
            <input v-model="selectedService.base_price" type="number" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Time Required (in minutes):</label>
            <input v-model="selectedService.time_required" type="number" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Description:</label>
            <textarea v-model="selectedService.description" class="form-control" required></textarea>
          </div>
          <button type="submit" class="btn btn-success">Save Changes</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { BASE_URL } from "../base.js";
export default {
  data() {
    return {
      services: [], // Holds the services data from the API
      isEditModalVisible: false,
      selectedService: null, // Holds the currently selected service for editing
    };
  },

  async created() {
    const res = await fetch(`${ BASE_URL }/admindashboard/servicesview`, {
      headers: { 'Authentication-Token': this.$store.state.auth_token },
    });

    if (res.ok) {
      this.services = await res.json();
    }
  },

  methods: {
    openEditModal(service) {
      // Open the edit modal and prefill selected service details
      this.selectedService = { ...service };
      this.isEditModalVisible = true;
    },
    closeEditModal() {
      // Close the edit modal
      this.isEditModalVisible = false;
      this.selectedService = null;
    },
    async updateService() {
      // Send updated service details to the server
      try {
        const res = await fetch(`${ BASE_URL }/admindashboard/service/${this.selectedService.id}`, {
          method: 'PATCH',
          headers: {
            'Authentication-Token': this.$store.state.auth_token,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.selectedService),
        });

        if (res.ok) {
          alert('Service updated successfully!');
          this.closeEditModal();
          this.refreshServices();
        } else {
          console.error('Error updating service');
        }
      } catch (error) {
        console.error('Error updating service:', error);
      }
    },
    async deleteService(serviceId) {
      // Delete a service
      if (!confirm('Are you sure you want to delete this service?')) return;

      try {
        const res = await fetch(`${ BASE_URL }/admindashboard/service/${serviceId}`, {
          method: 'DELETE',
          headers: { 'Authentication-Token': this.$store.state.auth_token },
        });

        if (res.ok) {
          alert('Service deleted successfully!');
          this.refreshServices();
        } else {
          console.error('Error deleting service');
        }
      } catch (error) {
        console.error('Error deleting service:', error);
      }
    },
    async refreshServices() {
      // Fetch the updated list of services
      const res = await fetch(`${ BASE_URL }/admindashboard/servicesview`, {
        headers: { 'Authentication-Token': this.$store.state.auth_token },
      });

      if (res.ok) {
        this.services = await res.json();
      }
    },
    logout() {
      this.$store.commit("logout");
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 600px;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 18px;
}

.card {
  border-radius: 8px;
  overflow: hidden;
}

.card-body {
  padding: 20px;
}

.card-title,
.card-text {
  margin-bottom: 10px;
}

.btn {
  margin-top: 10px;
}

button:hover {
  opacity: 0.8;
}

form .form-control {
  margin-bottom: 15px;
}
</style>
