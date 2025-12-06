import mysql.connector

# Koneksi ke database polusi
conn = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="",
    database="polusi"
)

# Membuat cursor
c = conn.cursor()

# ========== FUNGSI UNTUK NEGARA ==========
def view_all_negara():
    """Ambil semua data negara"""
    c.execute('''
        SELECT id_negara, nama_negara, benua, populasi
        FROM Negara
        ORDER BY nama_negara ASC
    ''')
    return c.fetchall()

def view_negara_by_id(id_negara):
    """Ambil data negara berdasarkan ID"""
    c.execute('''
        SELECT id_negara, nama_negara, benua, populasi
        FROM Negara
        WHERE id_negara = %s
    ''', (id_negara,))
    return c.fetchone()

def view_negara_by_benua(benua):
    """Ambil negara berdasarkan benua"""
    c.execute('''
        SELECT id_negara, nama_negara, benua, populasi
        FROM Negara
        WHERE benua = %s
        ORDER BY nama_negara ASC
    ''', (benua,))
    return c.fetchall()

# ========== FUNGSI UNTUK KOTA ==========
def view_all_kota():
    """Ambil semua data kota dengan nama negara"""
    c.execute('''
        SELECT 
            k.id_kota,
            k.nama_kota,
            k.populasi,
            n.nama_negara,
            n.benua
        FROM Kota k
        JOIN Negara n ON k.id_negara = n.id_negara
        ORDER BY k.nama_kota ASC
    ''')
    return c.fetchall()

def view_kota_by_negara(id_negara):
    """Ambil kota berdasarkan negara"""
    c.execute('''
        SELECT 
            k.id_kota,
            k.nama_kota,
            k.populasi,
            n.nama_negara
        FROM Kota k
        JOIN Negara n ON k.id_negara = n.id_negara
        WHERE k.id_negara = %s
        ORDER BY k.nama_kota ASC
    ''', (id_negara,))
    return c.fetchall()

# ========== FUNGSI UNTUK POLUSI ==========
def view_all_polusi():
    """Ambil semua data polusi dengan detail negara dan kota"""
    c.execute('''
        SELECT 
            p.id_polusi,
            n.nama_negara,
            k.nama_kota,
            p.tahun,
            p.indeks_kualitas_udara,
            p.indeks_karbon,
            p.indeks_ozon,
            p.indeks_nitrogen_dioksida
        FROM Polusi p
        JOIN Negara n ON p.id_negara = n.id_negara
        LEFT JOIN Kota k ON p.id_kota = k.id_kota
        ORDER BY p.tahun DESC, n.nama_negara ASC
    ''')
    return c.fetchall()

def view_polusi_by_negara(id_negara):
    """Ambil data polusi berdasarkan negara"""
    c.execute('''
        SELECT 
            p.id_polusi,
            n.nama_negara,
            k.nama_kota,
            p.tahun,
            p.indeks_kualitas_udara,
            p.indeks_karbon,
            p.indeks_ozon,
            p.indeks_nitrogen_dioksida
        FROM Polusi p
        JOIN Negara n ON p.id_negara = n.id_negara
        LEFT JOIN Kota k ON p.id_kota = k.id_kota
        WHERE p.id_negara = %s
        ORDER BY p.tahun DESC
    ''', (id_negara,))
    return c.fetchall()

def view_polusi_by_kota(id_kota):
    """Ambil data polusi berdasarkan kota"""
    c.execute('''
        SELECT 
            p.id_polusi,
            n.nama_negara,
            k.nama_kota,
            p.tahun,
            p.indeks_kualitas_udara,
            p.indeks_karbon,
            p.indeks_ozon,
            p.indeks_nitrogen_dioksida
        FROM Polusi p
        JOIN Negara n ON p.id_negara = n.id_negara
        JOIN Kota k ON p.id_kota = k.id_kota
        WHERE p.id_kota = %s
        ORDER BY p.tahun DESC
    ''', (id_kota,))
    return c.fetchall()

def view_polusi_by_tahun(tahun):
    """Ambil data polusi berdasarkan tahun"""
    c.execute('''
        SELECT 
            p.id_polusi,
            n.nama_negara,
            k.nama_kota,
            p.tahun,
            p.indeks_kualitas_udara,
            p.indeks_karbon,
            p.indeks_ozon,
            p.indeks_nitrogen_dioksida
        FROM Polusi p
        JOIN Negara n ON p.id_negara = n.id_negara
        LEFT JOIN Kota k ON p.id_kota = k.id_kota
        WHERE p.tahun = %s
        ORDER BY n.nama_negara ASC
    ''', (tahun,))
    return c.fetchall()

# ========== FUNGSI UNTUK KUALITAS HIDUP ==========
def view_all_kualitas_hidup():
    """Ambil semua data kualitas hidup"""
    c.execute('''
        SELECT 
            kh.id_kualitas_hidup,
            n.nama_negara,
            kh.tahun,
            kh.indeks_kualitas_hidup,
            kh.indeks_keamanan,
            kh.indeks_kesehatan,
            kh.indeks_pendidikan,
            kh.indeks_biaya_hidup
        FROM KualitasHidup kh
        JOIN Negara n ON kh.id_negara = n.id_negara
        ORDER BY kh.tahun DESC, n.nama_negara ASC
    ''')
    return c.fetchall()

def view_kualitas_hidup_by_negara(id_negara):
    """Ambil data kualitas hidup berdasarkan negara"""
    c.execute('''
        SELECT 
            kh.id_kualitas_hidup,
            n.nama_negara,
            kh.tahun,
            kh.indeks_kualitas_hidup,
            kh.indeks_keamanan,
            kh.indeks_kesehatan,
            kh.indeks_pendidikan,
            kh.indeks_biaya_hidup
        FROM KualitasHidup kh
        JOIN Negara n ON kh.id_negara = n.id_negara
        WHERE kh.id_negara = %s
        ORDER BY kh.tahun DESC
    ''', (id_negara,))
    return c.fetchall()

def view_kualitas_hidup_by_tahun(tahun):
    """Ambil data kualitas hidup berdasarkan tahun"""
    c.execute('''
        SELECT 
            kh.id_kualitas_hidup,
            n.nama_negara,
            kh.tahun,
            kh.indeks_kualitas_hidup,
            kh.indeks_keamanan,
            kh.indeks_kesehatan,
            kh.indeks_pendidikan,
            kh.indeks_biaya_hidup
        FROM KualitasHidup kh
        JOIN Negara n ON kh.id_negara = n.id_negara
        WHERE kh.tahun = %s
        ORDER BY n.nama_negara ASC
    ''', (tahun,))
    return c.fetchall()

# ========== FUNGSI AGREGASI & ANALISIS ==========
def get_avg_polusi_by_negara():
    """Rata-rata polusi per negara"""
    c.execute('''
        SELECT 
            n.nama_negara,
            AVG(p.indeks_kualitas_udara) as avg_kualitas_udara,
            AVG(p.indeks_karbon) as avg_karbon,
            AVG(p.indeks_ozon) as avg_ozon,
            AVG(p.indeks_nitrogen_dioksida) as avg_nitrogen_dioksida
        FROM Polusi p
        JOIN Negara n ON p.id_negara = n.id_negara
        GROUP BY n.nama_negara
        ORDER BY avg_kualitas_udara DESC
    ''')
    return c.fetchall()

def get_avg_kualitas_hidup_by_negara():
    """Rata-rata kualitas hidup per negara"""
    c.execute('''
        SELECT 
            n.nama_negara,
            AVG(kh.indeks_kualitas_hidup) as avg_kualitas_hidup,
            AVG(kh.indeks_keamanan) as avg_keamanan,
            AVG(kh.indeks_kesehatan) as avg_kesehatan,
            AVG(kh.indeks_pendidikan) as avg_pendidikan,
            AVG(kh.indeks_biaya_hidup) as avg_biaya_hidup
        FROM KualitasHidup kh
        JOIN Negara n ON kh.id_negara = n.id_negara
        GROUP BY n.nama_negara
        ORDER BY avg_kualitas_hidup DESC
    ''')
    return c.fetchall()

def get_tren_polusi_by_negara(id_negara):
    """Tren polusi per tahun untuk suatu negara"""
    c.execute('''
        SELECT 
            p.tahun,
            AVG(p.indeks_kualitas_udara) as avg_kualitas_udara,
            AVG(p.indeks_karbon) as avg_karbon,
            AVG(p.indeks_ozon) as avg_ozon,
            AVG(p.indeks_nitrogen_dioksida) as avg_nitrogen_dioksida
        FROM Polusi p
        WHERE p.id_negara = %s
        GROUP BY p.tahun
        ORDER BY p.tahun ASC
    ''', (id_negara,))
    return c.fetchall()

def get_kota_terpolusi(limit=10):
    """Kota dengan polusi tertinggi"""
    c.execute('''
        SELECT 
            k.nama_kota,
            n.nama_negara,
            AVG(p.indeks_kualitas_udara) as avg_kualitas_udara
        FROM Polusi p
        JOIN Kota k ON p.id_kota = k.id_kota
        JOIN Negara n ON p.id_negara = n.id_negara
        GROUP BY k.nama_kota, n.nama_negara
        ORDER BY avg_kualitas_udara DESC
        LIMIT %s
    ''', (limit,))
    return c.fetchall()

def get_benua():
    """Ambil daftar benua"""
    c.execute('''
        SELECT DISTINCT benua
        FROM Negara
        ORDER BY benua ASC
    ''')
    return c.fetchall()

def get_tahun():
    """Ambil daftar tahun yang tersedia"""
    c.execute('''
        SELECT DISTINCT tahun
        FROM Polusi
        ORDER BY tahun ASC
    ''')
    return c.fetchall()