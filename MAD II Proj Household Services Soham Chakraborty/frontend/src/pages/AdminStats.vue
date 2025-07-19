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
  <div class="container my-4">
    
    <h1 class="text-center mb-4">Admin Statistics</h1>

    <!-- Summary Section -->
    <div class="row g-3">
      <div class="col-md-3">
        <div class="card shadow-sm border-primary">
          <div class="card-body text-center">
            <h5 class="card-title">Total Customers</h5>
            <p class="display-6 text-primary">{{ totalCustomers }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card shadow-sm border-success">
          <div class="card-body text-center">
            <h5 class="card-title">Total Professionals</h5>
            <p class="display-6 text-success">{{ totalProfessionals }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card shadow-sm border-danger">
          <div class="card-body text-center">
            <h5 class="card-title">Blocked Customers</h5>
            <p class="display-6 text-danger">{{ blockedCustomers }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card shadow-sm border-warning">
          <div class="card-body text-center">
            <h5 class="card-title">Blocked Professionals</h5>
            <p class="display-6 text-warning">{{ blockedProfessionals }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="row mt-4">
      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Service Requests Overview</h5>
          </div>
          <div class="card-body">
            <canvas id="barChart"></canvas>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-header bg-warning text-dark">
            <h5 class="mb-0">Professional Distribution by Service</h5>
          </div>
          <div class="card-body">
            <canvas id="pieChart"></canvas>
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
      totalCustomers: 0,
      totalProfessionals: 0,
      blockedCustomers: 0,
      blockedProfessionals: 0,
      barChartData: null,
      pieChartData: null,
      barChart: null,
      pieChart: null,
    };
  },
  async created() {
    await this.fetchStatistics();
    this.$nextTick(() => {
      this.renderBarChart();
      this.renderPieChart();
    });
  },
  methods: {
    async fetchStatistics() {
      try {
        const res = await fetch(`${ BASE_URL }/admindashboard/statistics`, {
          headers: { "Authentication-Token": this.$store.state.auth_token },
        });
        if (res.ok) {
          const data = await res.json();
          this.totalCustomers = data.totalCustomers;
          this.totalProfessionals = data.totalProfessionals;
          this.blockedCustomers = data.blockedCustomers;
          this.blockedProfessionals = data.blockedProfessionals;
          this.barChartData = data.serviceRequests;
          this.pieChartData = data.professionalDistribution;
        } else {
          throw new Error("Failed to fetch statistics");
        }
      } catch (error) {
        console.error("Error fetching statistics:", error);
      }
    },
    renderBarChart() {
      if (!this.barChartData) return;
      const ctx = document.getElementById("barChart").getContext("2d");
      if (this.barChart) this.barChart.destroy();
      this.barChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["Ongoing Requests", "Closed Requests"],
          datasets: [
            {
              label: "Service Requests",
              data: [this.barChartData.ongoing, this.barChartData.closed],
              backgroundColor: ["rgba(75, 192, 192, 0.7)", "rgba(153, 102, 255, 0.7)"],
              borderColor: ["rgba(75, 192, 192, 1)", "rgba(153, 102, 255, 1)"],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1, precision: 0 },
            },
          },
          plugins: { legend: { display: false } },
        },
      });
    },
    renderPieChart() {
      if (!this.pieChartData) return;
      const ctx = document.getElementById("pieChart").getContext("2d");
      if (this.pieChart) this.pieChart.destroy();
      this.pieChart = new Chart(ctx, {
        type: "pie",
        data: {
          labels: Object.keys(this.pieChartData),
          datasets: [
            {
              data: Object.values(this.pieChartData),
              backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0"],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "bottom" } },
        },
      });
    },
    logout() {
      this.$store.commit("logout");
      this.$router.push("/login");
    },
  },
};
</script>

<style>
.card {
  border-radius: 10px;
}
canvas {
  max-width: 100%;
  height: 300px !important;
}
</style>
