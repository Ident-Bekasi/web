<!DOCTYPE html>
<html>
<head>
<title>Perhitungan Waktu Kematian</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script>
const bodyTempInput = document.getElementById("bodyTemp");
const ambientTempInput = document.getElementById("ambientTemp");
const clothingSelect = document.getElementById("clothing");
const genderSelect = document.getElementById("gender");
const weightInput = document.getElementById("weight"); // Get weight input element
const ageInput = document.getElementById("age"); // Get age input element
const calculateBtn = document.getElementById("calculate");
const resultDiv = document.getElementById("result");
const printBtn = document.getElementById("print");

let lastCalculation = null;

const kValues = {
    none: 1.0,
    light: 0.9,
    medium: 0.7,
    heavy: 0.5,
};

calculateBtn.addEventListener("click", () => {
    const bodyTemp = parseFloat(bodyTempInput.value);
    const ambientTemp = parseFloat(ambientTempInput.value);
    const clothing = clothingSelect.value;
    const gender = genderSelect.value;
    const weight = parseFloat(weightInput.value); // Get weight value
    const age = parseInt(ageInput.value); // Get age value
    let k = kValues[clothing];

    if (isNaN(bodyTemp) || isNaN(ambientTemp) || isNaN(weight) || isNaN(age) || bodyTemp < 0 || bodyTemp > 40 || ambientTemp < -20 || ambientTemp > 50) {
        resultDiv.textContent = "Input tidak valid. Pastikan semua suhu, berat badan, dan usia berada dalam rentang yang valid.";
        resultDiv.classList.remove("hidden", "text-orange-400");
        resultDiv.classList.add("text-red-600");
        return;
    }

    // Adjust k based on gender
    if (gender === 'female') {
        k *= 0.95; // Example adjustment: 5% slower cooling for females
    } else if (gender === 'male') {
        k *= 1.05; // Example adjustment: 5% faster cooling for males
    }

    // Adjust k based on weight (larger bodies cool slower)
    if (weight < 50) {
        k *= 1.1; // Lighter bodies cool faster
    } else if (weight > 90) {
        k *= 0.9; // Heavier bodies cool slower
    }

    // Adjust k based on age (children and elderly might cool differently)
    if (age < 10) {
        k *= 1.15; // Children cool faster due to higher surface area to volume ratio
    } else if (age > 70) {
        k *= 1.05; // Elderly might cool slightly faster due to less insulation
    }

    const denominator = k * (37 - ambientTemp);

    if (denominator <= 0) {
        resultDiv.textContent = "Input suhu lingkungan, jenis pakaian, jenis kelamin, berat badan, dan usia menghasilkan perhitungan tidak valid. Mohon periksa kembali.";
        resultDiv.classList.remove("hidden", "text-orange-400");
        resultDiv.classList.add("text-red-600");
        return;
    }

    const timeSinceDeath = (37 - bodyTemp) / denominator;
    const timeRounded = Math.max(0, timeSinceDeath).toFixed(2);

    resultDiv.textContent = `Perkiraan waktu kematian adalah sekitar ${timeRounded} jam yang lalu. Mengalihkan ke form data korban...`;
    resultDiv.classList.remove("hidden", "text-red-600");
    resultDiv.classList.add("text-orange-400");

    // Redirect after 2 seconds
    setTimeout(() => {
        window.location.href = 'victim_form.html';
    }, 2000);

    lastCalculation = {
        bodyTemp,
        ambientTemp,
        clothing,
        gender,
        weight, // Store weight
        age, // Store age
        k,
        timeRounded,
    };

    printBtn.disabled = false; // Enable the print button after calculation
});

printBtn.addEventListener("click", () => {
    if (!lastCalculation) return; // Ensure there is a calculation to print

    const { bodyTemp, ambientTemp, clothing, gender, weight, age, k, timeRounded } = lastCalculation;

    // Deskripsi jenis pakaian
    const clothingDesc = {
        none: "Tidak memakai pakaian",
        light: "Pakaian ringan (kaos, baju tipis)",
        medium: "Pakaian sedang (kemeja, jaket tipis)",
        heavy: "Pakaian tebal (jaket tebal, mantel)",
    };

    // Gender description map
    const genderDesc = {
        male: "Laki-laki",
        female: "Perempuan",
    };

    const doc = new jsPDF();
    const marginLeft = 15;
    let y = 20;

    doc.setTextColor(249, 115, 22);
    doc.setFontSize(18);
    doc.text("Laporan Perkiraan Waktu Kematian", marginLeft, y);
    y += 12;

    doc.setDrawColor(249, 115, 22);
    doc.setLineWidth(0.5);
    doc.line(marginLeft, y, 195, y);
    y += 10;

    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Suhu Tubuh Korban: ${bodyTemp} °C`, marginLeft, y);
    y += 8;
    doc.text(`Suhu Lingkungan: ${ambientTemp} °C`, marginLeft, y);
    y += 8;
    doc.text(`Jenis Pakaian Korban: ${clothingDesc[clothing]}`, marginLeft, y);
    y += 8;
    doc.text(`Jenis Kelamin Korban: ${genderDesc[gender]}`, marginLeft, y);
    y += 8;
    doc.text(`Berat Badan Korban: ${weight} kg`, marginLeft, y); // Add weight to PDF
    y += 8;
    doc.text(`Usia Korban: ${age} tahun`, marginLeft, y); // Add age to PDF
    y += 12;

    doc.setFontSize(14);
    doc.setTextColor(249, 115, 22);
    doc.text("Hasil Perhitungan:", marginLeft, y);
    y += 10;

    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Perkiraan waktu kematian adalah sekitar ${timeRounded} jam yang lalu.`, marginLeft, y);
    y += 15;

    doc.setFontSize(14);
    doc.setTextColor(249, 115, 22);
    doc.text("Rumus yang digunakan:", marginLeft, y);
    y += 10;

    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    const formulaLines = [
        "Waktu kematian (jam) = (37 - suhu tubuh korban) / (k × (37 - suhu lingkungan))",
        "",
        "Dimana:",
        "- k adalah koefisien berdasarkan jenis pakaian, jenis kelamin, berat badan, dan usia:",
        "  • Tidak memakai pakaian (none) = 1.0",
        "  • Pakaian ringan (light) = 0.9",
        "  • Pakaian sedang (medium) = 0.7",
        "  • Pakaian tebal (heavy) = 0.5",
        "  • Penyesuaian jenis kelamin: Perempuan (k * 0.95), Laki-laki (k * 1.05)",
        "  • Penyesuaian berat badan: <50kg (k * 1.1), >90kg (k * 0.9)",
        "  • Penyesuaian usia: <10 tahun (k * 1.15), >70 tahun (k * 1.05)",
        "",
        `Nilai k yang digunakan: ${k.toFixed(2)} (Pakaian: ${clothingDesc[clothing]}, Kelamin: ${genderDesc[gender]}, Berat: ${weight}kg, Usia: ${age}thn)`, // Update k display
    ];

    formulaLines.forEach((line) => {
        if (y > 280) { // Jika mencapai batas halaman, tambahkan halaman baru
            doc.addPage();
            y = 20;
        }
        doc.text(line, marginLeft, y);
        y += 7;
    });

    doc.save("Laporan_Perkiraan_Waktu_Kematian.pdf"); // Simpan PDF
});
</script>
</head>
<body>
<h1>Perhitungan Waktu Kematian</h1>
<label for="bodyTemp">Suhu Tubuh Korban (°C):</label>
<input type="number" id="bodyTemp"><br><br>
<label for="ambientTemp">Suhu Lingkungan (°C):</label>
<input type="number" id="ambientTemp"><br><br>
<label for="clothing">Jenis Pakaian:</label>
<select id="clothing">
    <option value="none">Tidak memakai pakaian</option>
    <option value="light">Pakaian ringan</option>
    <option value="medium">Pakaian sedang</option>
    <option value="heavy">Pakaian tebal</option>
</select><br><br>
<label for="gender">Jenis Kelamin:</label>
<select id="gender">
    <option value="male">Laki-laki</option>
    <option value="female">Perempuan</option>
</select><br><br>
<label for="weight">Berat Badan (kg):</label>
<input type="number" id="weight"><br><br>
<label for="age">Usia (tahun):</label>
<input type="number" id="age"><br><br>
<button id="calculate">Hitung</button>
<div id="result" class="hidden"></div>
<button id="print" disabled>Cetak Laporan</button>
</body>
</html>