# Kennitoring

A High-Performance System & Docker Monitoring Solution for Resource-Constrained Nodes.

---

## Overview

Kennitoring is a lightweight, real-time monitoring dashboard designed for edge infrastructure and home laboratories (e.g., Intel NUC, Raspberry Pi). Unlike heavy monitoring stacks (Prometheus/Grafana), Kennitoring operates with a near-zero footprint, providing essential telemetry without exhausting system resources.

It was specifically developed to monitor a decentralized home laboratory running high-load services like Wireguard, Xray, and Samba on low-power Intel Celeron/Pentium hardware.

---

## Key Technical Features

* **Smart Interface Filtering:** Automatically excludes ephemeral Docker bridge interfaces (br-*), virtual Ethernet pairs (veth*), and loopback devices to focus on physical (NIC) and tunnel (VPN) throughput.

* **Volatile Telemetry History:** Implements st.session_state with collections.deque to maintain a rolling history of CPU and RAM utilization without persistent database overhead.

* **Docker Engine Integration:** Communicates directly with the Docker socket via docker-py to provide real-time container status and orchestration insights.

* **Resource Optimization:** Uses @st.cache_resource for singleton Docker client instances to prevent socket exhaustion on low-memory systems.

* **Hardware-Agnostic Storage Tracking:** Deduplicates mount points by physical device ID, ensuring accurate reporting for complex partition layouts.

---

## Infrastructure Architecture

### The dashboard is designed to run as a standalone service or within a container, providing a unified view of: ###

* **Host Performance:** Global and per-core CPU load, Memory pressure.

* **Network Topology:** Real-time I/O tracking for physical and overlay networks (e.g., Wireguard).

* **Storage Health:** Disk usage metrics for physical volumes, excluding loopback/snap devices.

* **Container Management:** Live status of the local Docker microservices stack.

---

## Technology Stack & Environment

The project is developed and optimized for a specific heterogeneous infrastructure, ensuring stability across various hardware architectures.

### Software Stack
* **Language:** Python 3.10+
* **UI Framework:** Streamlit (Custom CSS injection for dense information density)
* **System Telemetry:** `psutil` (Low-level process and system utilities)
* **Container Orchestration:** `docker-py` (Docker Engine API SDK)
* **Data Handling:** `pandas` & `collections.deque` for time-series simulation

### Reference Hardware (Production Environment)
The system is actively maintained and tested on the following nodes:
* **CPU:** Intel® Celeron j3455.
* **RAM:** 4GB DDR3
* **Disk:** HDD Toshiba 1TB
The system demonstrated good performance on this stack. CPU usage was 2-5%, RAM usage was 150 MB.

---

## Installation & Deployment

### Prerequisites
*Python 3.10 or higher*
*Docker Engine with accessible /var/run/docker.sock*

## Setup:

```bash
# Clone the repository
git clone https://github.com/your-username/kennitoring.git
cd kennitoring

# Install core dependencies
pip install -r requirements.txt

# Launch the monitoring engine
streamlit run monitor.py --server.port 8501 --server.address 0.0.0.0

```

## Docker Deployment (Recommended):

```bash
docker run -d \
  --name kennitoring \
  --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -p 8501:8501 \
  efimr/kennitoring:latest

```

---

## Roadmap:

* **[ ] Container Control:** Integration of Start/Stop/Restart triggers via UI.

* **[ ] Alerting:** Telegram/Webhook notifications for resource threshold breaches.

* **[ ] Sensors:** Thermal monitoring for NVMe and CPU packages.

---

*Author: Efim Romanchenko – Software Engineer & Researcher.*