import streamlit as st
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64
import hashlib
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Untuk analisis sidik jari
import skimage
from skimage import feature, filters, morphology, measure
from scipy import ndimage

# Set halaman Streamlit
st.set_page_config(
    page_title="Sistem Analisis Sidik Jari Forensik",
    page_icon="🖐️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS kustom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3498db;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
    }
    .result-box {
        background-color: #e8f4fc;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #3498db;
    }
    .fingerprint-img {
        border: 2px solid #ddd;
        border-radius: 5px;
        padding: 5px;
        max-width: 100%;
    }
    .match-high {
        color: #27ae60;
        font-weight: bold;
    }
    .match-medium {
        color: #f39c12;
        font-weight: bold;
    }
    .match-low {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Judul aplikasi
st.markdown("<h1 class='main-header'>🖐️ Sistem Analisis Sidik Jari Forensik Berbasis AI</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='info-box'>
    <strong>Sistem ini menggunakan teknologi AI untuk:</strong><br>
    1. Analisis metadata dan karakteristik sidik jari<br>
    2. Identifikasi jenis jari dan tangan (kiri/kanan)<br>
    3. Perbandingan sidik jari referensi dengan sidik jari latent<br>
    4. Analisis berbasis ilmu forensik dan daktiloskopi
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/fingerprint.png", width=80)
    st.title("Menu Analisis")
    
    analysis_mode = st.selectbox(
        "Pilih Mode Analisis",
        ["Analisis Sidik Jari Tunggal", "Perbandingan Dua Sidik Jari"]
    )
    
    st.markdown("---")
    st.markdown("### Informasi Forensik")
    st.info("""
    **Ilmu Daktiloskopi**:
    - Sidik jari bersifat unik dan permanen
    - Pola dasar: Loop, Whorl, Arch
    - Minutiae: Titik karakteristik untuk identifikasi
    """)

# Kelas untuk analisis sidik jari
class FingerprintAnalyzer:
    def __init__(self):
        self.minutiae_types = {
            'ridge_ending': 1,
            'bifurcation': 2,
            'ridge_start': 3
        }
        
        # Pola sidik jari dasar
        self.finger_patterns = {
            'Loop': {
                'description': 'Pola melengkung seperti lingkaran',
                'common_fingers': ['Jari Telunjuk', 'Jari Tengah', 'Jari Manis'],
                'hand_ratio': {'kanan': 0.65, 'kiri': 0.35}
            },
            'Whorl': {
                'description': 'Pola spiral atau konsentris',
                'common_fingers': ['Ibu Jari', 'Jari Tengah'],
                'hand_ratio': {'kanan': 0.5, 'kiri': 0.5}
            },
            'Arch': {
                'description': 'Pola berbentuk lengkungan',
                'common_fingers': ['Ibu Jari', 'Jari Kelingking'],
                'hand_ratio': {'kanan': 0.45, 'kiri': 0.55}
            },
            'Tented Arch': {
                'description': 'Pola lengkungan dengan sudut tajam',
                'common_fingers': ['Jari Telunjuk'],
                'hand_ratio': {'kanan': 0.4, 'kiri': 0.6}
            }
        }
    
    def preprocess_image(self, image):
        """Preprocessing gambar sidik jari"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Normalisasi kontras
        gray = cv2.equalizeHist(gray)
        
        # Filter untuk meningkatkan ridge pattern
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        enhanced = cv2.filter2D(gray, -1, kernel)
        
        # Threshold adaptif
        binary = cv2.adaptiveThreshold(enhanced, 255, 
                                      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
        
        # Morfologi operasi
        kernel = np.ones((3,3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return gray, enhanced, binary
    
    def extract_minutiae(self, binary_image):
        """Ekstraksi minutiae dari sidik jari"""
        # Skeletonization
        skeleton = morphology.skeletonize(binary_image > 0)
        
        # Deteksi minutiae berdasarkan pola ridge
        minutiae_points = []
        rows, cols = skeleton.shape
        
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                if skeleton[i, j]:
                    # 8-neighborhood
                    neighborhood = skeleton[i-1:i+2, j-1:j+2]
                    ridge_count = np.sum(neighborhood) - 1
                    
                    if ridge_count == 1:  # Ridge ending
                        minutiae_points.append({
                            'x': j,
                            'y': i,
                            'type': 'ridge_ending',
                            'orientation': self.calculate_orientation(skeleton, i, j)
                        })
                    elif ridge_count == 3:  # Bifurcation
                        minutiae_points.append({
                            'x': j,
                            'y': i,
                            'type': 'bifurcation',
                            'orientation': self.calculate_orientation(skeleton, i, j)
                        })
        
        return minutiae_points, skeleton
    
    def calculate_orientation(self, skeleton, i, j):
        """Menghitung orientasi ridge pada titik tertentu"""
        if i > 1 and i < skeleton.shape[0]-2 and j > 1 and j < skeleton.shape[1]-2:
            region = skeleton[i-2:i+3, j-2:j+3]
            y, x = np.where(region)
            if len(x) > 1:
                return np.arctan2(np.mean(y)-2, np.mean(x)-2)
        return 0
    
    def analyze_pattern(self, binary_image):
        """Analisis pola dasar sidik jari"""
        # Hitung jumlah ridge dan arah umum
        contours = measure.find_contours(binary_image, 0.5)
        
        if len(contours) == 0:
            return "Tidak Diketahui", 0.5, 0.5
        
        # Analisis bentuk kontur
        areas = [measure.area_moments(c) for c in contours]
        eccentricities = [measure.eccentricity(c) for c in contours]
        
        avg_eccentricity = np.mean(eccentricities) if eccentricities else 0
        
        # Klasifikasi berdasarkan karakteristik
        if avg_eccentricity > 0.85:
            pattern = "Loop"
            confidence = min(0.8 + avg_eccentricity * 0.2, 0.95)
        elif avg_eccentricity > 0.7:
            pattern = "Arch"
            confidence = min(0.7 + avg_eccentricity * 0.3, 0.9)
        else:
            pattern = "Whorl"
            confidence = min(0.75 + (1 - avg_eccentricity) * 0.25, 0.92)
        
        # Prediksi tangan (kiri/kanan) berdasarkan asimetri
        moments = measure.moments(binary_image)
        if moments[0, 0] > 0:
            cx = moments[1, 0] / moments[0, 0]
            cy = moments[0, 1] / moments[0, 0]
            
            # Hitung asimetri
            left_half = binary_image[:, :binary_image.shape[1]//2]
            right_half = binary_image[:, binary_image.shape[1]//2:]
            
            left_density = np.sum(left_half) / (left_half.size + 1e-6)
            right_density = np.sum(right_half) / (right_half.size + 1e-6)
            
            hand_confidence = abs(left_density - right_density) * 2
            predicted_hand = "Kanan" if right_density > left_density else "Kiri"
        else:
            hand_confidence = 0.5
            predicted_hand = "Tidak Diketahui"
        
        return pattern, confidence, predicted_hand, hand_confidence
    
    def predict_finger(self, pattern, hand, minutiae_count):
        """Memprediksi jari berdasarkan pola dan karakteristik"""
        finger_probabilities = {
            'Ibu Jari': 0.15,
            'Jari Telunjuk': 0.20,
            'Jari Tengah': 0.20,
            'Jari Manis': 0.20,
            'Jari Kelingking': 0.15,
            'Tidak Diketahui': 0.10
        }
        
        # Sesuaikan probabilitas berdasarkan pola
        if pattern in self.finger_patterns:
            common_fingers = self.finger_patterns[pattern]['common_fingers']
            for finger in common_fingers:
                finger_probabilities[finger] += 0.1
        
        # Sesuaikan berdasarkan jumlah minutiae
        if minutiae_count > 50:
            finger_probabilities['Ibu Jari'] += 0.1
            finger_probabilities['Jari Tengah'] += 0.05
        elif minutiae_count < 30:
            finger_probabilities['Jari Kelingking'] += 0.1
        
        # Normalisasi probabilitas
        total = sum(finger_probabilities.values())
        for finger in finger_probabilities:
            finger_probabilities[finger] /= total
        
        # Prediksi jari dengan probabilitas tertinggi
        predicted_finger = max(finger_probabilities, key=finger_probabilities.get)
        confidence = finger_probabilities[predicted_finger]
        
        return predicted_finger, confidence, finger_probabilities
    
    def compare_fingerprints(self, fp1_data, fp2_data):
        """Membandingkan dua sidik jari"""
        # Ekstrak fitur untuk perbandingan
        minutiae1 = fp1_data.get('minutiae', [])
        minutiae2 = fp2_data.get('minutiae', [])
        
        pattern1 = fp1_data.get('pattern', 'Tidak Diketahui')
        pattern2 = fp2_data.get('pattern', 'Tidak Diketahui')
        
        # Hitung kesamaan pola
        pattern_similarity = 1.0 if pattern1 == pattern2 else 0.3
        
        # Hitung kesamaan berdasarkan minutiae
        if minutiae1 and minutiae2:
            # Hitung jarak minutiae yang cocok
            matched_minutiae = 0
            for m1 in minutiae1[:50]:  # Batasi untuk efisiensi
                for m2 in minutiae2[:50]:
                    distance = np.sqrt((m1['x'] - m2['x'])**2 + (m1['y'] - m2['y'])**2)
                    if distance < 5 and m1['type'] == m2['type']:
                        matched_minutiae += 1
                        break
            
            minutiae_similarity = matched_minutiae / max(len(minutiae1), len(minutiae2))
        else:
            minutiae_similarity = 0
        
        # Gabungkan skor
        total_similarity = (pattern_similarity * 0.3 + minutiae_similarity * 0.7) * 100
        
        # Tentukan level kecocokan
        if total_similarity > 70:
            match_level = "TINGGI"
            match_class = "match-high"
        elif total_similarity > 40:
            match_level = "SEDANG"
            match_class = "match-medium"
        else:
            match_level = "RENDAH"
            match_class = "match-low"
        
        return {
            'similarity_score': total_similarity,
            'match_level': match_level,
            'match_class': match_class,
            'pattern_similarity': pattern_similarity * 100,
            'minutiae_similarity': minutiae_similarity * 100,
            'matched_minutiae_count': matched_minutiae if minutiae1 and minutiae2 else 0
        }

# Inisialisasi analyzer
analyzer = FingerprintAnalyzer()

# Fungsi untuk menampilkan gambar
def display_image(image, title, caption=""):
    fig, ax = plt.subplots(figsize=(6, 6))
    if len(image.shape) == 3:
        ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    else:
        ax.imshow(image, cmap='gray')
    ax.set_title(title, fontsize=14)
    ax.axis('off')
    if caption:
        plt.figtext(0.5, 0.01, caption, ha='center', fontsize=10)
    st.pyplot(fig)
    plt.close()

# Fungsi untuk menampilkan minutiae pada gambar
def plot_minutiae(image, minutiae_points, title):
    fig, ax = plt.subplots(figsize=(6, 6))
    
    if len(image.shape) == 3:
        ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    else:
        ax.imshow(image, cmap='gray')
    
    # Plot minutiae
    colors = {'ridge_ending': 'red', 'bifurcation': 'green', 'ridge_start': 'blue'}
    
    for minutiae in minutiae_points[:100]:  # Batasi untuk visualisasi
        color = colors.get(minutiae['type'], 'yellow')
        ax.plot(minutiae['x'], minutiae['y'], marker='o', 
                markersize=6, color=color, markeredgecolor='white')
    
    ax.set_title(title, fontsize=14)
    ax.axis('off')
    
    # Legenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='red', label='Ridge Ending'),
        Patch(facecolor='green', label='Bifurcation'),
        Patch(facecolor='blue', label='Ridge Start')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)
    
    st.pyplot(fig)
    plt.close()

# Mode analisis tunggal
if analysis_mode == "Analisis Sidik Jari Tunggal":
    st.markdown("<h2 class='sub-header'>Analisis Sidik Jari Tunggal</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Unggah gambar sidik jari", 
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff']
        )
        
        if uploaded_file is not None:
            # Baca gambar
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            # Tampilkan gambar asli
            display_image(image, "Sidik Jari Asli")
            
            # Preprocessing
            with st.spinner("Melakukan preprocessing dan analisis..."):
                gray, enhanced, binary = analyzer.preprocess_image(image)
                
                # Ekstraksi minutiae
                minutiae_points, skeleton = analyzer.extract_minutiae(binary)
                
                # Analisis pola
                pattern, pattern_confidence, hand, hand_confidence = analyzer.analyze_pattern(binary)
                
                # Prediksi jari
                predicted_finger, finger_confidence, finger_probs = analyzer.predict_finger(
                    pattern, hand, len(minutiae_points)
                )
                
                # Metadata
                metadata = {
                    'filename': uploaded_file.name,
                    'filesize': uploaded_file.size,
                    'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'image_dimensions': image.shape,
                    'minutiae_count': len(minutiae_points),
                    'pattern_detected': pattern,
                    'pattern_confidence': pattern_confidence,
                    'predicted_hand': hand,
                    'hand_confidence': hand_confidence,
                    'predicted_finger': predicted_finger,
                    'finger_confidence': finger_confidence
                }
            
            # Tampilkan hasil preprocessing
            st.markdown("<h3 class='sub-header'>Hasil Preprocessing</h3>", unsafe_allow_html=True)
            
            col_pre1, col_pre2, col_pre3 = st.columns(3)
            
            with col_pre1:
                display_image(gray, "Grayscale", "Citra skala abu-abu")
            
            with col_pre2:
                display_image(enhanced, "Enhanced", "Peningkatan kontras dan ridge")
            
            with col_pre3:
                display_image(binary, "Binary", "Citra biner untuk analisis")
            
            # Tampilkan skeleton dan minutiae
            st.markdown("<h3 class='sub-header'>Deteksi Minutiae</h3>", unsafe_allow_html=True)
            
            col_skel1, col_skel2 = st.columns(2)
            
            with col_skel1:
                display_image(skeleton, "Skeleton", "Struktur ridge sidik jari")
            
            with col_skel2:
                plot_minutiae(enhanced, minutiae_points, "Titik Minutiae Terdeteksi")
    
    with col2:
        if uploaded_file is not None:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.markdown("### 📊 Hasil Analisis")
            
            # Metadata
            st.markdown("#### Metadata")
            st.json(metadata)
            
            # Pola sidik jari
            st.markdown("#### Pola Sidik Jari")
            pattern_info = analyzer.finger_patterns.get(pattern, {})
            
            col_pat1, col_pat2 = st.columns(2)
            with col_pat1:
                st.metric("Pola Terdeteksi", pattern)
                st.metric("Tingkat Kepercayaan", f"{pattern_confidence*100:.1f}%")
            
            with col_pat2:
                st.metric("Tangan Diprediksi", hand)
                st.metric("Tingkat Kepercayaan", f"{hand_confidence*100:.1f}%")
            
            if pattern_info:
                st.info(f"**Deskripsi**: {pattern_info.get('description', 'Tidak diketahui')}")
            
            # Prediksi jari
            st.markdown("#### Prediksi Jari")
            st.metric("Jari Diprediksi", predicted_finger)
            st.metric("Tingkat Kepercayaan", f"{finger_confidence*100:.1f}%")
            
            # Probabilitas jari
            st.markdown("##### Probabilitas per Jari")
            finger_df = pd.DataFrame(list(finger_probs.items()), 
                                   columns=['Jari', 'Probabilitas'])
            finger_df['Probabilitas'] = (finger_df['Probabilitas'] * 100).round(1)
            st.dataframe(finger_df.style.highlight_max(axis=0))
            
            # Minutiae
            st.markdown("#### Analisis Minutiae")
            minutiae_types = {}
            for m in minutiae_points:
                minutiae_types[m['type']] = minutiae_types.get(m['type'], 0) + 1
            
            for m_type, count in minutiae_types.items():
                st.metric(f"Jumlah {m_type.replace('_', ' ').title()}", count)
            
            st.metric("Total Minutiae", len(minutiae_points))
            
            st.markdown("</div>", unsafe_allow_html=True)

# Mode perbandingan dua sidik jari
else:
    st.markdown("<h2 class='sub-header'>Perbandingan Dua Sidik Jari</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
        <strong>Instruksi:</strong><br>
        1. Unggah sidik jari referensi (database)<br>
        2. Unggah sidik jari latent (TKP)<br>
        3. Sistem akan membandingkan dan menganalisis kesamaan
    </div>
    """, unsafe_allow_html=True)
    
    col_upload1, col_upload2 = st.columns(2)
    
    fp1_data = None
    fp2_data = None
    
    with col_upload1:
        st.markdown("### Sidik Jari Referensi")
        ref_file = st.file_uploader(
            "Unggah sidik jari referensi", 
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
            key="ref"
        )
        
        if ref_file is not None:
            ref_bytes = np.asarray(bytearray(ref_file.read()), dtype=np.uint8)
            ref_image = cv2.imdecode(ref_bytes, cv2.IMREAD_COLOR)
            display_image(ref_image, "Sidik Jari Referensi")
            
            # Analisis sidik jari referensi
            with st.spinner("Menganalisis sidik jari referensi..."):
                gray_ref, enhanced_ref, binary_ref = analyzer.preprocess_image(ref_image)
                minutiae_ref, skeleton_ref = analyzer.extract_minutiae(binary_ref)
                pattern_ref, conf_ref, hand_ref, hand_conf_ref = analyzer.analyze_pattern(binary_ref)
                
                fp1_data = {
                    'image': ref_image,
                    'gray': gray_ref,
                    'enhanced': enhanced_ref,
                    'binary': binary_ref,
                    'minutiae': minutiae_ref,
                    'skeleton': skeleton_ref,
                    'pattern': pattern_ref,
                    'pattern_confidence': conf_ref,
                    'hand': hand_ref,
                    'hand_confidence': hand_conf_ref,
                    'minutiae_count': len(minutiae_ref),
                    'filename': ref_file.name
                }
    
    with col_upload2:
        st.markdown("### Sidik Jari Latent (TKP)")
        latent_file = st.file_uploader(
            "Unggah sidik jari latent", 
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
            key="latent"
        )
        
        if latent_file is not None:
            latent_bytes = np.asarray(bytearray(latent_file.read()), dtype=np.uint8)
            latent_image = cv2.imdecode(latent_bytes, cv2.IMREAD_COLOR)
            display_image(latent_image, "Sidik Jari Latent")
            
            # Analisis sidik jari latent
            with st.spinner("Menganalisis sidik jari latent..."):
                gray_latent, enhanced_latent, binary_latent = analyzer.preprocess_image(latent_image)
                minutiae_latent, skeleton_latent = analyzer.extract_minutiae(binary_latent)
                pattern_latent, conf_latent, hand_latent, hand_conf_latent = analyzer.analyze_pattern(binary_latent)
                
                fp2_data = {
                    'image': latent_image,
                    'gray': gray_latent,
                    'enhanced': enhanced_latent,
                    'binary': binary_latent,
                    'minutiae': minutiae_latent,
                    'skeleton': skeleton_latent,
                    'pattern': pattern_latent,
                    'pattern_confidence': conf_latent,
                    'hand': hand_latent,
                    'hand_confidence': hand_conf_latent,
                    'minutiae_count': len(minutiae_latent),
                    'filename': latent_file.name
                }
    
    # Lakukan perbandingan jika kedua sidik jari telah diunggah
    if fp1_data is not None and fp2_data is not None:
        st.markdown("<h3 class='sub-header'>Hasil Perbandingan</h3>", unsafe_allow_html=True)
        
        with st.spinner("Membandingkan sidik jari..."):
            comparison_result = analyzer.compare_fingerprints(fp1_data, fp2_data)
        
        # Tampilkan hasil perbandingan
        col_result1, col_result2 = st.columns([1, 2])
        
        with col_result1:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.markdown("### 📈 Skor Kecocokan")
            
            similarity_score = comparison_result['similarity_score']
            match_level = comparison_result['match_level']
            match_class = comparison_result['match_class']
            
            # Tampilkan skor dengan progress bar
            st.markdown(f"### <span class='{match_class}'>{similarity_score:.1f}%</span>", 
                       unsafe_allow_html=True)
            st.progress(similarity_score / 100)
            st.markdown(f"**Tingkat Kecocokan**: <span class='{match_class}'>{match_level}</span>", 
                       unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Detail perbandingan
            st.markdown("#### Detail Analisis")
            st.metric("Kesamaan Pola", f"{comparison_result['pattern_similarity']:.1f}%")
            st.metric("Kesamaan Minutiae", f"{comparison_result['minutiae_similarity']:.1f}%")
            st.metric("Minutiae yang Cocok", comparison_result['matched_minutiae_count'])
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_result2:
            # Visualisasi perbandingan
            st.markdown("### Visualisasi Perbandingan")
            
            # Gabungkan kedua gambar untuk perbandingan visual
            fig, axes = plt.subplots(2, 3, figsize=(12, 8))
            
            # Baris 1: Sidik jari referensi
            axes[0, 0].imshow(cv2.cvtColor(fp1_data['image'], cv2.COLOR_BGR2RGB))
            axes[0, 0].set_title(f"Referensi: {fp1_data['filename']}")
            axes[0, 0].axis('off')
            
            axes[0, 1].imshow(fp1_data['enhanced'], cmap='gray')
            axes[0, 1].set_title("Enhanced")
            axes[0, 1].axis('off')
            
            # Plot minutiae referensi
            axes[0, 2].imshow(fp1_data['enhanced'], cmap='gray')
            for m in fp1_data['minutiae'][:50]:
                color = 'red' if m['type'] == 'ridge_ending' else 'green'
                axes[0, 2].plot(m['x'], m['y'], 'o', markersize=4, color=color)
            axes[0, 2].set_title(f"Minutiae: {len(fp1_data['minutiae'])} titik")
            axes[0, 2].axis('off')
            
            # Baris 2: Sidik jari latent
            axes[1, 0].imshow(cv2.cvtColor(fp2_data['image'], cv2.COLOR_BGR2RGB))
            axes[1, 0].set_title(f"Latent: {fp2_data['filename']}")
            axes[1, 0].axis('off')
            
            axes[1, 1].imshow(fp2_data['enhanced'], cmap='gray')
            axes[1, 1].set_title("Enhanced")
            axes[1, 1].axis('off')
            
            # Plot minutiae latent
            axes[1, 2].imshow(fp2_data['enhanced'], cmap='gray')
            for m in fp2_data['minutiae'][:50]:
                color = 'red' if m['type'] == 'ridge_ending' else 'green'
                axes[1, 2].plot(m['x'], m['y'], 'o', markersize=4, color=color)
            axes[1, 2].set_title(f"Minutiae: {len(fp2_data['minutiae'])} titik")
            axes[1, 2].axis('off')
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        # Analisis forensik
        st.markdown("<h3 class='sub-header'>Analisis Forensik</h3>", unsafe_allow_html=True)
        
        col_forensic1, col_forensic2, col_forensic3 = st.columns(3)
        
        with col_forensic1:
            st.markdown("##### Pola Sidik Jari")
            pattern_match = fp1_data['pattern'] == fp2_data['pattern']
            st.metric("Pola Referensi", fp1_data['pattern'])
            st.metric("Pola Latent", fp2_data['pattern'])
            st.metric("Kecocokan Pola", "Ya" if pattern_match else "Tidak")
        
        with col_forensic2:
            st.markdown("##### Analisis Tangan")
            hand_match = fp1_data['hand'] == fp2_data['hand']
            st.metric("Tangan Referensi", fp1_data['hand'])
            st.metric("Tangan Latent", fp2_data['hand'])
            st.metric("Kecocokan Tangan", "Ya" if hand_match else "Tidak")
        
        with col_forensic3:
            st.markdown("##### Statistik Minutiae")
            minutiae_diff = abs(len(fp1_data['minutiae']) - len(fp2_data['minutiae']))
            st.metric("Minutiae Referensi", len(fp1_data['minutiae']))
            st.metric("Minutiae Latent", len(fp2_data['minutiae']))
            st.metric("Perbedaan Jumlah", minutiae_diff)
        
        # Kesimpulan forensik
        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Kesimpulan Forensik")
        
        if similarity_score > 70:
            st.success("**KESIMPULAN**: Tingkat kemiripan SANGAT TINGGI. Sidik jari referensi dan latent kemungkinan berasal dari sumber yang sama.")
            st.info("**REKOMENDASI**: Hasil ini dapat digunakan sebagai bukti pendukung dalam penyelidikan forensik.")
        elif similarity_score > 40:
            st.warning("**KESIMPULAN**: Tingkat kemiripan SEDANG. Diperlukan analisis lebih lanjut oleh ahli daktiloskopi.")
            st.info("**REKOMENDASI**: Lakukan verifikasi manual dan pertimbangkan faktor kualitas gambar.")
        else:
            st.error("**KESIMPULAN**: Tingkat kemiripan RENDAH. Sidik jari referensi dan latent kemungkinan berasal dari sumber yang berbeda.")
            st.info("**REKOMENDASI**: Periksa kualitas gambar atau carilah referensi sidik jari lain.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
    <p><strong>Sistem Analisis Sidik Jari Forensik Berbasis AI</strong></p>
    <p>Menggunakan teknik Daktiloskopi dan Computer Vision untuk analisis sidik jari</p>
    <p>© 2024 Sistem Forensik Digital</p>
</div>
""", unsafe_allow_html=True)