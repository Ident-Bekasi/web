// Membuat partikel latar belakang
function createParticles() {
    const container = document.getElementById('particles');
    const particleCount = 30;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Ukuran dan posisi acak
        const size = Math.random() * 20 + 5;
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}vw`;
        particle.style.top = `${posY}vh`;
        
        // Warna acak (cyan atau magenta)
        const color = Math.random() > 0.5 ? '0, 247, 255' : '255, 0, 255';
        particle.style.background = `rgba(${color}, ${0.2 + Math.random() * 0.3})`;
        particle.style.boxShadow = `0 0 20px rgba(${color}, 0.5)`;
        
        // Animasi dengan durasi acak
        const duration = Math.random() * 20 + 15;
        particle.style.animationDuration = `${duration}s`;
        
        container.appendChild(particle);
    }
}

// Algoritma estimasi waktu kematian (sederhana)
function estimateTimeOfDeath(data) {
    // Faktor dasar: penurunan suhu tubuh rata-rata 0.8°C per jam
    let baseRate = 0.8;
    
    // Penyesuaian berdasarkan faktor lingkungan dan individu
    let adjustment = 1.0;
    
    // Pengaruh pakaian
    const clothingFactors = {
        'none': 1.2,
        'light': 1.1,
        'medium': 1.0,
        'heavy': 0.8
    };
    adjustment *= clothingFactors[data.clothing];
    
    // Pengaruh bentuk tubuh
    const bodyTypeFactors = {
        'thin': 1.1,
        'normal': 1.0,
        'overweight': 0.9,
        'obese': 0.8
    };
    adjustment *= bodyTypeFactors[data.bodyType];
    
    // Pengaruh lingkungan (air vs darat)
    if (data.environment === 'water') {
        adjustment *= 2.0; // Lebih cepat di air
    }
    
    // Pengaruh kelembaban
    adjustment *= (1 + (data.humidity - 50) / 200);
    
    // Pengaruh angin
    adjustment *= (1 + data.wind / 50);
    
    // Pengaruh posisi ditemukan
    const positionFactors = {
        'open': 1.1,
        'shaded': 0.9,
        'buried': 0.7
    };
    adjustment *= positionFactors[data.foundPosition];
    
    // Perbedaan suhu tubuh dengan lingkungan
    const tempDiff = 37 - data.bodyTemp; // Suhu normal tubuh 37°C
    const envDiff = 37 - data.envTemp;
    
    // Estimasi waktu (dalam jam)
    let estimatedHours = tempDiff / (baseRate * adjustment);
    
    // Jika lingkungan lebih dingin dari tubuh, perhitungan lebih kompleks
    if (data.envTemp < data.bodyTemp) {
        estimatedHours = tempDiff / (baseRate * adjustment * (1 + (37 - data.envTemp) / 20));
    }
    
    return Math.max(0, estimatedHours);
}

// Format hasil estimasi
function formatResult(hours) {
    if (hours === 0) {
        return "Kurang dari 1 jam";
    }
    
    const totalMinutes = Math.round(hours * 60);
    const days = Math.floor(totalMinutes / 1440);
    const hoursRemainder = Math.floor((totalMinutes % 1440) / 60);
    const minutes = totalMinutes % 60;
    
    if (days > 0) {
        return `${days} hari, ${hoursRemainder} jam, ${minutes} menit`;
    } else if (hoursRemainder > 0) {
        return `${hoursRemainder} jam, ${minutes} menit`;
    } else {
        return `${minutes} menit`;
    }
}

// Event listener untuk tombol hitung
document.getElementById('calculateBtn').addEventListener('click', function() {
    // Mengumpulkan data dari form
    const data = {
        bodyTemp: parseFloat(document.getElementById('bodyTemp').value),
        envTemp: parseFloat(document.getElementById('envTemp').value),
        gender: document.getElementById('gender').value,
        clothing: document.getElementById('clothing').value,
        bodyType: document.getElementById('bodyType').value,
        environment: document.getElementById('environment').value,
        humidity: parseFloat(document.getElementById('humidity').value),
        wind: parseFloat(document.getElementById('wind').value),
        foundPosition: document.getElementById('foundPosition').value
    };
    
    // Validasi input
    if (isNaN(data.bodyTemp) || isNaN(data.envTemp)) {
        alert('Masukkan suhu tubuh dan suhu lingkungan yang valid!');
        return;
    }
    
    // Melakukan estimasi
    const estimatedHours = estimateTimeOfDeath(data);
    const resultText = formatResult(estimatedHours);
    
    // Menampilkan hasil
    document.getElementById('result').textContent = resultText;
    document.getElementById('resultContainer').classList.add('show');
});

// Inisialisasi
window.addEventListener('load', function() {
    createParticles();
});