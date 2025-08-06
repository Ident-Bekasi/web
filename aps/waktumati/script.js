// Membuat partikel animasi
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 100;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Ukuran dan posisi acak
        const size = Math.random() * 6 + 2;
        const posX = Math.random() * 100;
        const delay = Math.random() * 15;
        const duration = Math.random() * 15 + 10;
        const direction = Math.random() > 0.5 ? 1 : -1;
        
        // Warna partikel (dengan variasi)
        const colors = [
            'rgba(0, 195, 255, 0.6)',
            'rgba(110, 0, 255, 0.5)',
            'rgba(255, 255, 255, 0.4)',
            'rgba(255, 204, 0, 0.4)'
        ];
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}%`;
        particle.style.animationDelay = `${delay}s`;
        particle.style.animationDuration = `${duration}s`;
        particle.style.setProperty('--direction', direction);
        particle.style.background = color;
        particle.style.boxShadow = `0 0 ${size*2}px ${color}`;
        
        particlesContainer.appendChild(particle);
    }
}

// Fungsi perhitungan waktu kematian
function calculateTimeOfDeath() {
    // Ambil nilai dari form
    const bodyTemp = parseFloat(document.getElementById('bodyTemp').value);
    const envTemp = parseFloat(document.getElementById('envTemp').value);
    const bodyWeight = parseFloat(document.getElementById('bodyWeight').value);
    
    // MODIFIKASI: Mengambil nilai dari elemen select
    const gender = document.getElementById('gender').value;
    
    // Jenis pakaian
    const selectedClothingOption = document.querySelector('.clothing-option.selected');
    const clothing = selectedClothingOption ? selectedClothingOption.dataset.value : ''; // Ambil nilai jika ada yang terpilih
    
    // Validasi input - Hanya tampilkan alert jika tombol hitung ditekan dan ada input yang kosong
    // Untuk perhitungan otomatis saat input berubah, kita akan membiarkan hasil 0.0 jika input tidak valid
    const isFormValid = !isNaN(bodyTemp) && !isNaN(envTemp) && !isNaN(bodyWeight) && gender !== "" && clothing !== "";

    if (!isFormValid) {
        // Jika form tidak valid, set hasil ke 0.0 dan keterangan default
        document.getElementById('timeResult').textContent = '0.0';
        document.getElementById('resultBodyTemp').textContent = 'Suhu tubuh mayat yang diukur.';
        document.getElementById('resultEnvTemp').textContent = 'Suhu rata-rata di sekitar lokasi penemuan.';
        document.getElementById('resultWeight').textContent = 'Berat badan perkiraan atau aktual korban.';
        document.getElementById('resultGender').textContent = 'Jenis kelamin korban untuk faktor koreksi.';
        document.getElementById('resultClothing').textContent = 'Kategori pakaian yang dikenakan korban.';
        return; // Hentikan eksekusi fungsi jika input tidak valid
    }
    
    // Faktor koreksi berdasarkan jenis kelamin
    let genderFactor;
    switch(gender) {
        case 'male': genderFactor = 1.0; break;
        case 'female': genderFactor = 0.9; break;
        case 'trans_male': genderFactor = 1.0; break; // Asumsi sama dengan male
        case 'trans_female': genderFactor = 0.9; break; // Asumsi sama dengan female
        case 'non_binary': genderFactor = 0.95; break; // Nilai tengah
        case 'unknown': genderFactor = 1.0; break; // Default ke male jika tidak diketahui
        default: genderFactor = 1.0;
    }
    
    // Faktor koreksi berdasarkan pakaian
    let clothingFactor;
    switch(clothing) {
        case 'light': clothingFactor = 1.2; break;
        case 'medium': clothingFactor = 1.0; break;
        case 'heavy': clothingFactor = 0.8; break;
        default: clothingFactor = 1.0;
    }
    
    // Faktor koreksi berdasarkan berat badan
    let weightFactor;
    if (bodyWeight < 50) {
        weightFactor = 1.3;
    } else if (bodyWeight >= 50 && bodyWeight < 80) {
        weightFactor = 1.1;
    } else {
        weightFactor = 1.0;
    }
    
    // Perhitungan waktu kematian (dalam jam)
    // Formula dasar: waktu = (37.2 - bodyTemp) / (0.05 * faktor_koreksi)
    // Dengan faktor koreksi = genderFactor * clothingFactor * weightFactor
    const baseCoolingRate = 0.05; // Tingkat pendinginan dasar (°C/jam)
    const initialBodyTemp = 37.2; // Suhu tubuh normal (°C)
    
    const coolingRate = baseCoolingRate * genderFactor * clothingFactor * weightFactor;
    const timeSinceDeath = (initialBodyTemp - bodyTemp) / coolingRate;
    
    // Tampilkan hasil
    document.getElementById('timeResult').textContent = timeSinceDeath.toFixed(1);
    document.getElementById('resultBodyTemp').textContent = `${bodyTemp} °C`;
    document.getElementById('resultEnvTemp').textContent = `${envTemp} °C`;
    document.getElementById('resultWeight').textContent = `${bodyWeight} kg`;
    
    let genderText;
    switch(gender) {
        case 'male': genderText = 'Pria'; break;
        case 'female': genderText = 'Wanita'; break;
        case 'trans_male': genderText = 'Trans Pria'; break;
        case 'trans_female': genderText = 'Trans Wanita'; break;
        case 'non_binary': genderText = 'Non-Biner'; break;
        case 'unknown': genderText = 'Tidak Diketahui'; break;
        default: genderText = '-';
    }
    document.getElementById('resultGender').textContent = genderText;
    
    let clothingText;
    switch(clothing) {
        case 'light': clothingText = 'Tipis'; break;
        case 'medium': clothingText = 'Sedang'; break;
        case 'heavy': clothingText = 'Tebal'; break;
        default: clothingText = '-';
    }
    document.getElementById('resultClothing').textContent = clothingText;
}

// Event listeners untuk tombol input data
document.querySelector('.victim-button').addEventListener('click', () => {
    window.location.href = 'formkorban.html'; // Arahkan ke formkorban.html
});

document.querySelector('.scene-button').addEventListener('click', () => {
    alert('Fitur Input Data TKP akan segera tersedia!'); // Tetap alert untuk TKP
});

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    
    // Pilih pakaian
    document.querySelectorAll('.clothing-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.clothing-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            this.classList.add('selected');
            calculateTimeOfDeath(); // Hitung ulang saat pilihan pakaian berubah
        });
    });
    
    // Tombol hitung
    document.getElementById('calculateBtn').addEventListener('click', () => {
        const bodyTemp = parseFloat(document.getElementById('bodyTemp').value);
        const envTemp = parseFloat(document.getElementById('envTemp').value);
        const bodyWeight = parseFloat(document.getElementById('bodyWeight').value);
        const gender = document.getElementById('gender').value;
        const selectedClothingOption = document.querySelector('.clothing-option.selected');
        const clothing = selectedClothingOption ? selectedClothingOption.dataset.value : '';

        if (isNaN(bodyTemp) || isNaN(envTemp) || isNaN(bodyWeight) || gender === "" || clothing === "") {
            alert('Harap masukkan semua nilai yang valid, termasuk Jenis Kelamin dan Jenis Pakaian!');
            return;
        }
        calculateTimeOfDeath(); // Lakukan perhitungan jika valid
    });
    
    // Hitung otomatis saat input berubah, tanpa alert jika kosong
    document.getElementById('bodyTemp').addEventListener('input', calculateTimeOfDeath);
    document.getElementById('envTemp').addEventListener('input', calculateTimeOfDeath);
    document.getElementById('bodyWeight').addEventListener('input', calculateTimeOfDeath);
    document.getElementById('gender').addEventListener('change', calculateTimeOfDeath); // Tambahkan event listener untuk dropdown gender

    // Panggil calculateTimeOfDeath() saat DOMContentLoaded untuk mengisi keterangan awal
    calculateTimeOfDeath();

    // Sidebar functionality
    const hamburgerMenu = document.getElementById('hamburgerMenu');
    const mobileSidebar = document.getElementById('mobileSidebar');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function openSidebar() {
        mobileSidebar.classList.add('open');
        sidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling body
    }

    function closeSidebarFunc() {
        mobileSidebar.classList.remove('open');
        sidebarOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Allow scrolling body
    }

    hamburgerMenu.addEventListener('click', openSidebar);
    closeSidebar.addEventListener('click', closeSidebarFunc);
    sidebarOverlay.addEventListener('click', closeSidebarFunc);
});
