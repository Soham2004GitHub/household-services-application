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

  <div class="dashboard-container">
    
    <div class="content">
      <section class="card shadow-sm">
        <h2 class="card-header bg-primary text-white">Customers</h2>
        <div class="card-body">
          <table v-if="customers.length" class="table table-striped table-hover">
            <thead class="table-dark">
              <tr>
                <th>Username</th>
                <th>Address</th>
                <th>Pincode</th>
                <th>Email</th>
                <th>Status</th>
                <th>Action</th>
                <th>Profile Picture</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="customer in customers" :key="customer.id">
                <td>{{ customer.name }}</td>
                <td>{{ customer.address }}</td>
                <td>{{ customer.pincode }}</td>
                <td>{{ customer.email }}</td>
                <td>
                  <span class="badge" :class="customer.active ? 'bg-success' : 'bg-danger'">
                    {{ customer.active ? 'Active' : 'Blocked' }}
                  </span>
                </td>
                <td>
                  <button 
                    class="btn btn-sm" 
                    :class="customer.active ? 'btn-danger' : 'btn-success'" 
                    @click="toggleActive(customer)">
                    {{ customer.active ? 'Block' : 'Unblock' }}
                  </button>
                </td>
                <td>
                  <button class="btn btn-info btn-sm" @click="viewProfilePic(customer)">View</button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted">No customers found</p>
        </div>
      </section>

      <section class="card shadow-sm mt-4">
        <h2 class="card-header bg-warning text-dark">Professionals</h2>
        <div class="card-body">
          <table v-if="professionals.length" class="table table-striped table-hover">
            <thead class="table-dark">
              <tr>
                <th>Username</th>
                <th>Address</th>
                <th>Pincode</th>
                <th>Email</th>
                <th>Status</th>
                <th>Verify</th>
                <th>Action</th>
                <th>Profile Picture</th>
                <th>Resume</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="professional in professionals" :key="professional.id">
                <td>{{ professional.name }}</td>
                <td>{{ professional.address }}</td>
                <td>{{ professional.pincode }}</td>
                <td>{{ professional.email }}</td>
                <td>
                  <span v-if="professional.verified" class="badge" :class="professional.active ? 'bg-success' : 'bg-danger'">
                    {{ professional.active ? 'Active' : 'Blocked' }}
                  </span>
                  <span v-else class="badge bg-secondary">Pending Verification</span>
                </td>
                <td>
                  <button class="btn btn-warning btn-sm" @click="verifyProfessional(professional)" :disabled="professional.verified">
                    Verify
                  </button>
                </td>
                <td>
                  <button 
                    class="btn btn-sm" 
                    :class="professional.active ? 'btn-danger' : 'btn-success'" 
                    :disabled="!professional.verified"
                    @click="toggleActive(professional)">
                    {{ professional.active ? 'Block' : 'Unblock' }}
                  </button>
                </td>
                <td>
                  <button class="btn btn-info btn-sm" @click="viewProfilePic(professional)">View</button>
                </td>
                <td>
                  <button class="btn btn-success btn-sm" @click="downloadResume(professional)">Download</button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted">No professionals found</p>
        </div>
      </section>
    </div>

    <!-- Profile Picture Modal -->
    <div v-if="profilePicUrl" class="modal fade show d-block" style="background: rgba(0,0,0,0.5);" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Profile Picture</h5>
            <button type="button" class="btn btn-secondary close-btn" @click="profilePicUrl = null">Close</button>
          </div>
          <div class="modal-body text-center">
            <img :src="profilePicUrl" alt="Profile Picture" class="img-fluid rounded shadow-lg" />
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
      customers: [],
      professionals: [],
      profilePicUrl: null
    };
  },
  methods: {
    async create_csv() {
      const res = await fetch(`${ BASE_URL }/create-csv`, {
        headers: { 'Authentication-Token': this.$store.state.auth_token }
      });
      const task_id = (await res.json()).task_id;

      const interval = setInterval(async () => {
        const res = await fetch(`${ BASE_URL }/get-csv/${task_id}`);
        if (res.ok) {
          window.open(`${ BASE_URL }/get-csv/${task_id}`);
          clearInterval(interval);
        }
      }, 100);
    },
    async toggleActive(user) {
      const endpoint = user.active ? "/blockuser/" : "/unblockuser/";
      try {
        const res = await fetch(`${ BASE_URL }${endpoint}${user.id}`, {
          method: "POST",
          headers: { "Authentication-Token": this.$store.state.auth_token }
        });
        if (res.ok) {
          await this.fetchUsers();
        }
      } catch (error) {
        console.error("Error toggling active status:", error);
      }
    },
    async verifyProfessional(professional) {
      try {
        const res = await fetch(`${ BASE_URL }/verifyprofessional/${professional.id}`, {
          method: "POST",
          headers: {
            "Authentication-Token": this.$store.state.auth_token,
          },
        });
        if (res.ok) {
          await this.fetchUsers(); // Refetch to update the state
          alert("Professional verified successfully");
        } else {
          alert("Failed to verify professional");
        }
      } catch (error) {
        console.error("Error verifying professional:", error);
        alert("An error occurred. Please try again.");
      }
    },
    async viewProfilePic(user) {
      try {
        const res = await fetch(`${ BASE_URL }/profilepic/${user.id}`, {
          headers: { "Authentication-Token": this.$store.state.auth_token },
        });
        if (res.ok) {
          const data = await res.json();
          this.profilePicUrl = `data:image/jpeg;base64,${data.profile_pic_base64}`;
        } else {
          alert("Failed to fetch profile picture");
        }
      } catch (error) {
        console.error("Error fetching profile picture:", error);
        alert("An error occurred. Please try again.");
      }
    },
    async downloadResume(professional) {
      try {
        const res = await fetch(`${ BASE_URL }/resume/${professional.id}`, {
          headers: { "Authentication-Token": this.$store.state.auth_token },
        });
        if (res.ok) {
          const blob = await res.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `${professional.name}_resume.pdf`;
          a.click();
          URL.revokeObjectURL(url);
        } else {
          alert("Failed to download resume");
        }
      } catch (error) {
        console.error("Error downloading resume:", error);
        alert("An error occurred. Please try again.");
      }
    },
    async fetchUsers() {
      try {
        const res = await fetch(`${ BASE_URL }/admindashboard/usersview`, {
          headers: { "Authentication-Token": this.$store.state.auth_token }
        });
        if (res.ok) {
          const users = await res.json();
          this.customers = users.filter(user => user.role === "customer");
          this.professionals = users.filter(user => user.role === "professional");
        }
      } catch (error) {
        console.error("Error fetching users:", error);
      }
    },
    logout() {
      this.$store.commit("logout");
      this.$router.push("/login");
    }
  },
  async created() {
    await this.fetchUsers();
  }
};
</script>

<style>
.dashboard-container {
  padding: 20px;
  background-color: #f8f9fa;
}
.card {
  border-radius: 10px;
  overflow: hidden;
}
.btn {
  transition: 0.3s ease;
}
.btn:hover {
  transform: scale(1.05);
}
.modal-content {
  border-radius: 10px;
}
</style>
