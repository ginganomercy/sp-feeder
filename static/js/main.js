/**
 * main.js - Menangani interaksi real-time untuk Smart Pet Feeder
 */

// 1. Fungsi untuk menampilkan Alert kustom (Pengganti alert browser)
function showAlert(message, type = 'success') {
    const container = document.getElementById('js-alert-container');
    if (!container) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show shadow-sm`;
    alertDiv.role = 'alert';
    alertDiv.style.borderRadius = "15px";
    alertDiv.style.border = "none";
    alertDiv.style.zIndex = "1050";
    
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} me-2"></i>
            <small class="fw-bold">${message}</small>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    container.appendChild(alertDiv);
    
    // Hilangkan otomatis setelah 4 detik
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 4000);
}

// 2. Fungsi Beri Makan Manual (Tombol 10g, 20g, 50g)
let isFeeding = false;

async function feedNow(deviceSn, porsi = 15) {
    if (isFeeding) return; 
    
    isFeeding = true;
    const buttons = document.querySelectorAll('.btn-warning');
    
    // Nonaktifkan tombol agar tidak bisa diklik berkali-kali (mencegah duplikasi dari sisi user)
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = "0.6";
    });

    try {
        showAlert(`Memproses pakan ${porsi}g...`, 'info');

        const response = await fetch('/api/feed_now', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_id: deviceSn, porsi: porsi })
        });

        const result = await response.json();
        if (result.status === 'success') {
            showAlert(`Berhasil! Pakan ${porsi}g sedang dikeluarkan.`, 'success');
            
            // Jeda 2 detik (lebih lama sedikit) agar backend selesai memproses MQTT 
            // dan database sudah benar-benar terupdate sebelum kita refresh halaman.
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showAlert("Gagal terhubung ke alat.", 'error');
            resetButtons();
        }
    } catch (error) {
        console.error("Error Feeding:", error);
        showAlert("Masalah koneksi ke server.", 'error');
        resetButtons();
    }
}

function resetButtons() {
    isFeeding = false;
    const buttons = document.querySelectorAll('.btn-warning');
    buttons.forEach(btn => {
        btn.disabled = false;
        btn.style.opacity = "1";
    });
}

// 3. Fungsi Reset Pengingat Air
function resetWaterTimer() {
    const btn = document.getElementById('water-btn');
    const text = document.getElementById('water-status');
    
    if (btn) btn.classList.remove('active');
    if (btn) btn.innerHTML = '<i class="fas fa-check"></i>';
    if (text) text.innerText = "Air sudah segar!";
    
    showAlert("Status air minum diperbarui.", "success");
    
    setTimeout(() => {
        if (btn) btn.innerHTML = '<i class="fas fa-tint"></i>';
    }, 3000);
}

// 4. Inisialisasi Visual saat halaman dimuat
document.addEventListener('DOMContentLoaded', () => {
    // Animasi Bar Pantry (Sisa Pakan)
    const fillElement = document.getElementById('pantry-fill');
    if (fillElement) {
        const targetHeight = fillElement.getAttribute('data-percent');
        setTimeout(() => {
            fillElement.style.height = targetHeight + '%';
        }, 500);
    }

    // Pastikan area riwayat dimulai dari posisi paling atas
    const logArea = document.querySelector('.log-scroll-area');
    if (logArea) logArea.scrollTop = 0;
});