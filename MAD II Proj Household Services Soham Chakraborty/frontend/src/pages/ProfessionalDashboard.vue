<template>
  <div>
    
      <nav class="navbar navbar-expand-lg navbar-dark bg-success shadow">
      <div class="container-fluid">
        <h1 class="text-left text-white">Professional Dashboard</h1>
        <div v-if="professional" class="ms-auto text-white text-lg">
          <strong>{{ professional.name }}</strong>
          <br>Address : {{ professional.address }}
          <br>Pincode : {{ professional.pincode }}
          <br>Service Type : {{ professional.service_type }}
          <br>Experience (in years) : {{ professional.experience }}
          <br>Rating : {{ professional.rating }}
        </div>
        <button class="btn btn-danger shadow-sm ms-auto" @click="logout">Logout</button>
      </div>
    </nav>
    <div class="container mt-4">
      <div class="mt-4">
      <section class="card shadow-sm mt-4">
        <h2 class="card-header bg-warning text-dark">Pending Service Requests</h2>
        <table v-if="pendingRequests.length" class="table table-striped table-hover shadow-sm">
          <thead class="table-dark">
            <tr>
              <th>ID</th>
              <th>Customer Name</th>
              <th>Address</th>
              <th>Pincode</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in pendingRequests" :key="req.id">
              <td>{{ req.id }}</td>
              <td>{{ req.customer_name }}</td>
              <td>{{ req.address }}</td>
              <td>{{ req.pincode }}</td>
              <td>
                <span class="badge bg-warning text-dark">{{ req.status }}</span>
              </td>
              <td>
                <button @click="updateServiceRequestStatus(req.id, 'Accepted')" class="btn btn-success btn-sm">Accept</button>
                <button @click="updateServiceRequestStatus(req.id, 'Rejected')" class="btn btn-danger btn-sm mx-2">Reject</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">No pending service requests</p>
        </section>


        <section class="card shadow-sm mt-4">
        <h2 class="card-header bg-primary text-light">Accepted Service Requests</h2>
        <table v-if="acceptedRequests.length" class="table table-striped table-hover shadow-sm">
          <thead class="table-dark">
            <tr>
              <th>ID</th>
              <th>Customer Name</th>
              <th>Address</th>
              <th>Pincode</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in acceptedRequests" :key="req.id">
              <td>{{ req.id }}</td>
              <td>{{ req.customer_name }}</td>
              <td>{{ req.address }}</td>
              <td>{{ req.pincode }}</td>
              <td>
                <span class="badge bg-primary">{{ req.status }}</span>
              </td>
              <td>
                <button @click="updateServiceRequestStatus(req.id, 'Completed')" class="btn btn-primary btn-sm">Mark Complete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">No accepted service requests</p>
        </section>

        <section class="card shadow-sm mt-4">
        <h2 class="card-header bg-success text-dark">Completed Service Requests</h2>
        <table v-if="completedRequests.length" class="table table-striped table-hover shadow-sm">
          <thead class="table-dark">
            <tr>
              <th>ID</th>
              <th>Customer Name</th>
              <th>Address</th>
              <th>Pincode</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in completedRequests" :key="req.id">
              <td>{{ req.id }}</td>
              <td>{{ req.customer_name }}</td>
              <td>{{ req.address }}</td>
              <td>{{ req.pincode }}</td>
              <td>
                <span class="badge bg-success">{{ req.status }} and Closed</span>
              </td>
              <td>
                <button @click="viewReview(req.id)" class="btn btn-info btn-sm">View Review</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">No completed service requests</p>
        </section>

        <section class="card shadow-sm mt-4">
        <h2 class="card-header bg-danger text-light">Rejected Service Requests</h2>
        <table v-if="rejectedRequests.length" class="table table-striped table-hover shadow-sm">
          <thead class="table-dark">
            <tr>
              <th>ID</th>
              <th>Customer Name</th>
              <th>Address</th>
              <th>Pincode</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in rejectedRequests" :key="req.id">
              <td>{{ req.id }}</td>
              <td>{{ req.customer_name }}</td>
              <td>{{ req.address }}</td>
              <td>{{ req.pincode }}</td>
              <td>
                <span class="badge bg-danger">{{ req.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">No rejected service requests</p>
        </section>

        <section class="card shadow-sm mt-4">
        <h2 class="card-header bg-secondary text-light">Cancelled Service Requests</h2>
        <table v-if="cancelledRequests.length" class="table table-striped table-hover shadow-sm">
          <thead class="table-dark">
            <tr>
              <th>ID</th>
              <th>Customer Name</th>
              <th>Address</th>
              <th>Pincode</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in cancelledRequests" :key="req.id">
              <td>{{ req.id }}</td>
              <td>{{ req.customer_name }}</td>
              <td>{{ req.address }}</td>
              <td>{{ req.pincode }}</td>
              <td>
                <span class="badge bg-secondary">{{ req.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">No cancelled service requests</p>
        </section>
      </div>
    </div>

    <!-- View Review Modal -->
    <div v-if="isReviewModalVisible" class="modal-overlay">
      <div class="modal-content">
        <button @click="closeReviewModal" class="btn btn-secondary close-btn">Close</button>
        <h3 class="text-center">Review Details</h3>
        <p v-if="reviewData.rating !== null" class="text-center">
          <strong>Rating:</strong> {{ reviewData.rating }}
        </p>
        <p v-else class="text-muted text-center">No rating available</p>
        <p v-if="reviewData.reviewText" class="text-center">
          <strong>Review:</strong> {{ reviewData.reviewText }}
        </p>
        <p v-else class="text-muted text-center">No review text available</p>
      </div>
    </div>
  </div>
</template>

<script>
import { BASE_URL } from "../base.js";
export default {
  data() {
    return {
      professional: {
        name: "",
        address: "",
        pincode: "",
        service_type: "",
        experience: "",
        rating: "",
      },
      pendingRequests: [],
      acceptedRequests: [],
      completedRequests: [],
      rejectedRequests: [],
      cancelledRequests: [],
      isReviewModalVisible: false,
      reviewData: {
        rating: null,
        reviewText: '',
      },
    };
  },
  async created() {
    if (!this.$store.getters.isAuthenticated) {
      this.$router.push('/login');
      return;
    }
    await this.refreshRequests();
  },
  methods: {
    async updateServiceRequestStatus(serviceRequestId, newStatus) {
      const professionalId = JSON.parse(localStorage.getItem('user')).id;
      try {
        const res = await fetch(`${ BASE_URL }/professionaldashboard/${professionalId}/servicerequests/${serviceRequestId}`, {
          method: "PATCH",
          headers: {
            "Authentication-Token": this.$store.state.auth_token,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ status: newStatus }),
        });
        if (res.ok) {
          alert("Service request status updated");
          await this.refreshRequests();
        } else {
          console.error("Error updating request:", await res.text());
        }
      } catch (error) {
        console.error("Error updating service request:", error);
      }
    },
    async refreshRequests() {
      const professionalId = JSON.parse(localStorage.getItem('user')).id;
      try {
        const res = await fetch(`${ BASE_URL }/professionaldashboard/${professionalId}/allservicerequests`, {
          headers: { 'Authentication-Token': this.$store.state.auth_token },
        });
        if (res.ok) {
          const data = await res.json();
          this.pendingRequests = data.Pending || [];
          this.acceptedRequests = data.Accepted || [];
          this.completedRequests = data.Completed || [];
          this.rejectedRequests = data.Rejected || [];
          this.cancelledRequests = data.Cancelled || [];
        }
        await this.fetchProfessionalDetails(professionalId)
      } catch (error) {
        console.error("Error refreshing requests:", error);
      }
    },
    async fetchProfessionalDetails(professionalID) {
      //const professionalId = JSON.parse(localStorage.getItem('user')).id;
      try {
        const res = await fetch(`${ BASE_URL }/professionalinfo/${professionalID}`, {
          headers: { 'Authentication-Token': this.$store.state.auth_token },
        });

      if (res.ok) {
        this.professional = await res.json();
        } else {
      console.error("Error fetching professional details:", await res.text());
      }
        } catch (error) {
      console.error("Error fetching professional details:", error);
      }
    },
    async viewReview(serviceRequestId) {
      try {
        const res = await fetch(`${ BASE_URL }/servicerequest/${serviceRequestId}/review`, {
          headers: { 'Authentication-Token': this.$store.state.auth_token },
        });
        if (res.ok) {
          this.reviewData = await res.json();
        } else {
          this.reviewData = { rating: null, reviewText: 'No review available.' };
        }
        this.isReviewModalVisible = true;
      } catch (error) {
        console.error("Error fetching review:", error);
        alert("An error occurred.");
      }
    },
    closeReviewModal() {
      this.isReviewModalVisible = false;
      this.reviewData = { rating: null, reviewText: '' };
    },
    logout() {
      this.$store.commit("logout"); // Call Vuex mutation to clear session storage
      this.$router.push("/login"); // Redirect to the home page
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
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 600px;
  width: 100%;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  border: none;
  color: #f9f9f9;
  cursor: pointer;
}

.table-striped tbody tr:nth-of-type(odd) {
  background-color: #f9f9f9;
}
.table-bordered th,
.table-bordered td {
  border: 1px solid #ddd;
}
.table-hover tbody tr:hover {
  background-color: #e9ecef;
}

.badge {
  font-size: 0.9rem;
  padding: 5px 10px;
  border-radius: 8px;
}

.btn {
  border-radius: 8px;
  transition: all 0.3s ease-in-out;
}

.btn:hover {
  transform: scale(1.05);
}

.text-primary {
  color: #007bff !important;
}

.text-warning {
  color: #ffc107 !important;
}

.text-success {
  color: #28a745 !important;
}

.text-info {
  color: #17a2b8 !important;
}

.text-danger {
  color: #dc3545 !important;
}

.text-secondary {
  color: #6c757d !important;
}

.shadow-sm {
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}
</style>

