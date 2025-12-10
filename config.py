import mysql.connector
from mysql.connector import Error
import pandas as pd

class DatabaseConfig:
    """Konfigurasi koneksi database"""

    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',  
        'database': 'polusi',
        'charset': 'utf8mb4'
    }

    COLORS = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff9800',
        'info': '#17a2b8',
        'purple': '#9467bd',
        'pink': '#e377c2',
        'brown': '#8c564b',
        'gray': '#7f7f7f'
    }
    
    COLOR_PALETTE = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    @staticmethod
    def get_connection():
        """Membuat koneksi ke database"""
        try:
            connection = mysql.connector.connect(**DatabaseConfig.DB_CONFIG)
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error koneksi database: {e}")
            return None
    
    @staticmethod
    def execute_query(query, params=None):
        """Eksekusi query dan return DataFrame"""
        connection = DatabaseConfig.get_connection()
        if connection:
            try:
                df = pd.read_sql(query, connection, params=params)
                return df
            except Error as e:
                print(f"Error eksekusi query: {e}")
                return pd.DataFrame()
            finally:
                if connection.is_connected():
                    connection.close()
        return pd.DataFrame()
    
    @staticmethod
    def get_negara_list():
        """Mendapatkan list negara"""
        query = "SELECT kode_negara, nama_negara, benua FROM negara ORDER BY nama_negara"
        return DatabaseConfig.execute_query(query)
    
    @staticmethod
    def get_kota_by_negara(kode_negara):
        """Mendapatkan list kota berdasarkan negara"""
        query = """
        SELECT k.id_kota, k.nama_kota, n.nama_negara
        FROM kota k
        JOIN negara n ON k.kode_negara = n.kode_negara
        WHERE k.kode_negara = %s
        ORDER BY k.nama_kota
        """
        return DatabaseConfig.execute_query(query, params=(str(kode_negara),))
    
    @staticmethod
    def get_all_kota():
        """Mendapatkan semua kota dengan info negara"""
        query = """
        SELECT k.id_kota, k.nama_kota, n.nama_negara, n.kode_negara
        FROM kota k
        JOIN negara n ON k.kode_negara = n.kode_negara
        ORDER BY n.nama_negara, k.nama_kota
        """
        return DatabaseConfig.execute_query(query)
    
    @staticmethod
    def get_polusi_data(id_kota=None, tahun=None):
        """Mendapatkan data polusi"""
        query = """
        SELECT p.*, k.nama_kota, n.nama_negara
        FROM polusi p
        JOIN kota k ON p.id_kota = k.id_kota
        JOIN negara n ON k.kode_negara = n.kode_negara
        WHERE 1=1
        """
        params = []
        
        if id_kota:
            query += " AND p.id_kota = %s"
            params.append(int(id_kota))
        
        if tahun:
            query += " AND p.tahun = %s"
            params.append(int(tahun))
        
        query += " ORDER BY p.tahun, k.nama_kota"
        
        return DatabaseConfig.execute_query(query, params=tuple(params) if params else None)
    
    @staticmethod
    def get_kualitas_hidup_data(id_kota=None, tahun=None):
        """Mendapatkan data kualitas hidup"""
        query = """
        SELECT kh.*, k.nama_kota, n.nama_negara
        FROM kualitas_hidup kh
        JOIN kota k ON kh.id_kota = k.id_kota
        JOIN negara n ON k.kode_negara = n.kode_negara
        WHERE 1=1
        """
        params = []
        
        if id_kota:
            query += " AND kh.id_kota = %s"
            params.append(int(id_kota))
        
        if tahun:
            query += " AND kh.tahun = %s"
            params.append(int(tahun))
        
        query += " ORDER BY kh.tahun, k.nama_kota"
        
        return DatabaseConfig.execute_query(query, params=tuple(params) if params else None)
    
    @staticmethod
    def get_populasi_kota(id_kota=None):
        """Mendapatkan data populasi kota"""
        query = """
        SELECT pk.*, k.nama_kota, n.nama_negara
        FROM populasi_kota pk
        JOIN kota k ON pk.id_kota = k.id_kota
        JOIN negara n ON k.kode_negara = n.kode_negara
        WHERE 1=1
        """
        params = []
        
        if id_kota:
            query += " AND pk.id_kota = %s"
            params.append(int(id_kota))
        
        query += " ORDER BY pk.tahun"
        
        return DatabaseConfig.execute_query(query, params=tuple(params) if params else None)
    
    @staticmethod
    def get_summary_stats():
        """Mendapatkan statistik ringkasan"""
        query = """
        SELECT 
            COUNT(DISTINCT n.kode_negara) as total_negara,
            COUNT(DISTINCT k.id_kota) as total_kota,
            COUNT(DISTINCT p.id_polusi) as total_data_polusi,
            COUNT(DISTINCT kh.id_kualitas_hidup) as total_data_kualitas,
            ROUND(AVG(p.index_kualitas_udara), 2) as avg_polusi,
            ROUND(AVG(kh.index_kualitas_hidup), 2) as avg_kualitas_hidup
        FROM negara n
        LEFT JOIN kota k ON n.kode_negara = k.kode_negara
        LEFT JOIN polusi p ON k.id_kota = p.id_kota
        LEFT JOIN kualitas_hidup kh ON k.id_kota = kh.id_kota
        """
        return DatabaseConfig.execute_query(query)