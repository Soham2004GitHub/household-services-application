<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-success shadow">
      <div class="container-fluid">
        <h1 class="text-left text-white">Customer Dashboard</h1>
        <div v-if="customer" class="ms-auto text-white text-lg">
          <strong>{{ customer.name }}</strong>
          <br>Address : {{ customer.address }}
          <br>Pincode : {{ customer.pincode }}
        </div>
        <button class="btn btn-danger shadow-sm ms-auto" @click="logout">Logout</button>
      </div>
    </nav>

    <div class="container mt-4">
      <!-- Search Bar -->
      <div class="search-bar mb-4 p-3 shadow-sm bg-light rounded">
        <div class="d-flex justify-content-between mb-2">
          <input v-model="search.name" class="form-control" placeholder="Search by Name" />
          <input v-model="search.address" class="form-control" placeholder="Search by Address" />
        </div>
        <div class="d-flex justify-content-between">
          <input v-model="search.pincode" type="number" class="form-control" placeholder="Search by Pincode" />
          <input v-model="search.service_type" class="form-control" placeholder="Search by Service Type" />
        </div>
        <button @click="searchProfessionals" class="btn btn-primary mt-3 w-100">Search</button>
      </div>

      <!-- Professionals List -->
      <section class="card shadow-sm mt-4">
        <h2 class="card-header bg-primary text-white">Professionals</h2>
        <table v-if="professionals.length" class="table table-striped table-hover shadow-sm">
          <thead class="table-dark">
            <tr>
              <th>Name</th>
              <th>Address</th>
              <th>Pincode</th>
              <th>Email</th>
              <th>Service</th>
              <th>Action</th>
              <th>Profile</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in professionals" :key="p.id">
              <td>{{ p.name }}</td>
              <td>{{ p.address }}</td>
              <td>{{ p.pincode }}</td>
              <td>{{ p.email }}</td>
              <td>{{ p.service_type }}</td>
              <td>
                <button @click="requestService(p)" class="btn btn-primary">Request Service</button>
              </td>
              <td>
                <button @click="viewProfile(p.id)" class="btn btn-info">View</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-center text-muted">No professionals found or unauthorized access.</p>
      </section>

      <!-- Service Requests Section -->
      <section class="card shadow-sm mt-4">
        <h2 class="card-header bg-warning text-dark">Your Service Requests</h2>
        <div class="card-body">
          <table v-if="serviceRequests.length" class="table table-striped table-hover">
            <thead class="table-dark">
              <tr>
                <th>Service Request ID</th>
                <th>Professional Name</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in serviceRequests" :key="req.id">
                <td>{{ req.id }}</td>
                <td>{{ req.professional_name }}</td>
                <td>{{ req.status }}</td>
                <td v-if="req.reviewed">Completed, Review Given and Closed</td>
                <td v-else>
                  <button v-if="req.status === 'Pending' || req.status === 'Accepted'" @click="cancelRequest(req.id)" class="btn btn-danger">Cancel</button>
                  <button v-if="req.status === 'Completed'" @click="leaveReview(req)" class="btn btn-warning">Leave Review</button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted">No service requests found.</p>
        </div>
      </section>

      <!-- Profile Modal -->
      <div v-if="isProfileModalVisible && professionalProfile" class="custom-modal-overlay">
        <div class="custom-modal">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="modal-title">Professional Profile</h5>
            <button class="btn btn-secondary close-btn" @click="closeProfileModal">Close</button>
          </div>
          <div class="p-3 text-center">
            <img :src="profileImage" alt="Profile Picture" class="img-fluid rounded shadow-lg mb-3" />
            <p><strong>Name:</strong> {{ professionalProfile.name }}</p>
            <p><strong>Description:</strong> {{ professionalProfile.description }}</p>
            <p><strong>Service Type:</strong> {{ professionalProfile.service_type }}</p>
            <p><strong>Experience:</strong> {{ professionalProfile.experience }} years</p>
          </div>
        </div>
      </div>

      <!-- Leave Review Modal -->
      <div v-if="isReviewModalVisible" class="custom-modal-overlay">
        <div class="custom-modal">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="modal-title">Leave a Review</h5>
            <button class="btn btn-secondary close-btn" @click="closeReviewModal">Close</button>
          </div>
          <div class="p-3">
            <form @submit.prevent="submitReview">
              <label for="rating">Rating (out of 5):</label>
              <input id="rating" type="number" v-model="reviewData.rating" min="0" max="5" step="1" required class="form-control mb-3" />
              <label for="reviewText">Review:</label>
              <textarea id="reviewText" v-model="reviewData.reviewText" rows="4" required class="form-control mb-3"></textarea>
              <button type="submit" class="btn btn-success w-100">Submit Review</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { BASE_URL } from "../base.js";

export default {
  data() {
    return {
      customer: {
        name: "",
        address: "",
        pincode: "",
        email: "",
      },
      professionals: [],
      serviceRequests: [],
      search: {
        name: '',
        address: '',
        pincode: '',
        service_type: '',
      },
      isProfileModalVisible: false,
      professionalProfile: null,
      isReviewModalVisible: false,
      reviewData: {
        requestId: null,
        rating: null,
        reviewText: '',
      },
    };
  },
  computed: {
    profileImage() {
      if (this.professionalProfile && this.professionalProfile.profile_pic) {
        const pic = this.professionalProfile.profile_pic.trim(); // Trim spaces
        return pic.startsWith("data:image") ? pic : `data:image/jpeg;base64,${pic}`;
      }
      return "default-profile.png"; // Fallback image
    }
  },  
  async created() {
    await this.fetchData();
  },
  methods: {
    
    async searchProfessionals() {
      try {
        const customerId = JSON.parse(localStorage.getItem('user')).id;
        const queryParams = new URLSearchParams(this.search).toString();
        const res = await fetch(`${ BASE_URL }/customerdashboard/${customerId}?${queryParams}`, {
          headers: { 'Authentication-Token': this.$store.state.auth_token },
        });
        this.professionals = res.ok ? await res.json() : [];
        if (!res.ok) {
          alert('No professionals found.');
          //fetchData()
        }
      } catch (error) {
        console.error('Error searching professionals:', error);
      }
    },
    async fetchData() {
      if (!this.$store.getters.isAuthenticated) {
        this.$router.push('/login');
        return;
      }

      try {
        const customerId = JSON.parse(localStorage.getItem('user')).id;
        await this.fetchCustomerInfo(customerId);
        const professionalsRes = await fetch(`${ BASE_URL }/customerdashboard/${customerId}`, {
          headers: { 'Authentication-Token': this.$store.state.auth_token },
        });
        this.professionals = professionalsRes.ok ? await professionalsRes.json() : [];

        const serviceRequestsRes = await fetch(`${ BASE_URL }/customerdashboard/servicerequests/${customerId}`, {
          headers: { 'Authentication-Token': this.$store.state.auth_token },
        });
        this.serviceRequests = serviceRequestsRes.ok ? await serviceRequestsRes.json() : [];
        
      } catch (error) {
        console.error('Error loading data:', error);
      }
    },
    async fetchCustomerInfo(customerId) {
      try {
        const response = await fetch(`${BASE_URL}/customerinfo/${customerId}`, {
        headers: { 'Authentication-Token': this.$store.state.auth_token },
        });

        if (response.ok) {
        this.customer = await response.json();
        } else {
       console.error('Failed to load customer info');
        }
      } catch (error) {
        console.error('Error loading customer info:', error);
        }
      },
    async requestService(professional) {
      try {
        const customerId = JSON.parse(localStorage.getItem('user')).id;
        const res = await fetch(`${ BASE_URL }/customer/${customerId}`, {
          headers: { 'Authentication-Token': this.$store.state.auth_token },
        });

        if (!res.ok) throw new Error('Failed to fetch customer data.');
        const customerData = await res.json();

        const serviceRequestDetails = {
          customerId,
          professionalId: professional.id,
          address: customerData.address,
          pincode: customerData.pincode,
        };

        const requestRes = await fetch(`${ BASE_URL }/servicerequest`, {
          method: 'POST',
          headers: {
            'Authentication-Token': this.$store.state.auth_token,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(serviceRequestDetails),
        });

        if (requestRes.ok) {
          alert('Service request created successfully!');
          await this.fetchData();
        } else {
          const errorResponse = await requestRes.json();
          console.error('Error Response:', errorResponse);
          alert('Error creating service request.');
        }
      } catch (error) {
        console.error('Error in requestService:', error);
        alert('Failed to create service request.');
      }
    },
    async viewProfile(professionalId) {
      try {
        const res = await fetch(`${BASE_URL}/professional/profile/${professionalId}`, {
          headers: { "Authentication-Token": this.$store.state.auth_token },
        });

        if (res.ok) {
          this.professionalProfile = await res.json();
          console.log("Profile Data:", this.professionalProfile); // Debugging
          this.isProfileModalVisible = true;
        } else {
          console.error("Error fetching profile data.");
          alert("Could not fetch profile details.");
        }
      } catch (error) {
        console.error("Error fetching profile:", error);
      }
    },
    closeProfileModal() {
      this.isProfileModalVisible = false;
    },
    async cancelRequest(requestId) {
      await fetch(`${ BASE_URL }/servicerequest/${requestId}/cancel`, { method: 'POST' });
      await this.fetchData();
    },
    leaveReview(request) {
      this.reviewData.requestId = request.id;
      this.isReviewModalVisible = true;
    },
    closeReviewModal() {
    this.isReviewModalVisible = false;
    this.reviewData = { requestId: null, rating: null, reviewText: '' };
    },
    async submitReview() {
      try {
        const res = await fetch(`${ BASE_URL }/servicerequest/${this.reviewData.requestId}/review`, {
          method: 'POST',
          headers: {
            'Authentication-Token': this.$store.state.auth_token,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            rating: this.reviewData.rating,
            reviewText: this.reviewData.reviewText,
          }),
        });

        if (res.ok) {
          alert('Review submitted successfully!');
          this.closeReviewModal();
          await this.fetchData();
        } else {
          console.error('Error submitting review:', await res.text());
          alert('Failed to submit review.');
        }
      } catch (error) {
        console.error('Error submitting review:', error);
        alert('An error occurred.');
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
.search-bar {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.search-bar input {
  margin-bottom: 10px;
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
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.custom-modal {
  background: white;
  width: 350px; /* Small modal width */
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
.modal-content {
  border-radius: 10px;
}




/*
.table-striped tbody tr:nth-of-type(odd) {
  background-color: #f9f9f9;
}





.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 60%;
  max-width: 600px;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
}
.profile-pic {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 20px;
}
*/
</style>
