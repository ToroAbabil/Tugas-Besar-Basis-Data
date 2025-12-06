CREATE DATABASE polusi
    DEFAULT CHARACTER SET = 'utf8mb4';

CREATE TABLE Negara (
    id_negara INT PRIMARY KEY,
    nama_negara VARCHAR(100),
    benua VARCHAR(100),
    populasi BIGINT
);

CREATE TABLE Kota (
    id_kota INT PRIMARY KEY,
    id_negara INT,
    nama_kota VARCHAR(100),
    populasi BIGINT,
    FOREIGN KEY (id_negara) REFERENCES Negara(id_negara)
);

CREATE TABLE Polusi (
    id_polusi INT PRIMARY KEY,
    id_negara INT,
    id_kota INT,
    tahun INT,
    indeks_kualitas_udara INT,
    indeks_karbon INT,
    indeks_ozon INT,
    indeks_nitrogen_dioksida INT,
    FOREIGN KEY (id_negara) REFERENCES Negara(id_negara),
    FOREIGN KEY (id_kota) REFERENCES Kota(id_kota)
);

CREATE TABLE KualitasHidup (
    id_kualitas_hidup INT PRIMARY KEY,
    id_negara INT,
    tahun INT,
    indeks_kualitas_hidup INT,
    indeks_keamanan INT,
    indeks_kesehatan INT,
    indeks_pendidikan INT,
    indeks_biaya_hidup INT,
    FOREIGN KEY (id_negara) REFERENCES Negara(id_negara)
);

INSERT INTO Negara (id_negara, nama_negara, benua, populasi) VALUES
(1, 'Amerika Serikat', 'Amerika Utara', 331000000),
(2, 'Kanada', 'Amerika Utara', 38000000),
(3, 'Jerman', 'Eropa', 83000000),
(4, 'Jepang', 'Asia', 125000000),
(5, 'Australia', 'Oseania', 25600000),
(6, 'India', 'Asia', 1380000000),
(7, 'Brasil', 'Amerika Selatan', 213000000),
(8, 'Inggris', 'Eropa', 67000000),
(9, 'Prancis', 'Eropa', 65000000),
(10, 'Indonesia', 'Asia', 273000000);

INSERT INTO Kota (id_kota, id_negara, nama_kota, populasi) VALUES
(1, 1, 'New York', 18800000),
(2, 1, 'Los Angeles', 12800000),
(3, 2, 'Toronto', 6300000),
(4, 2, 'Vancouver', 2600000),
(5, 3, 'Berlin', 3600000),
(6, 3, 'Hamburg', 1800000),
(7, 4, 'Tokyo', 37400000),
(8, 4, 'Osaka', 19000000),
(9, 5, 'Sydney', 5300000),
(10, 5, 'Melbourne', 5000000),
(11, 6, 'Delhi', 30200000),
(12, 6, 'Mumbai', 20700000),
(13, 7, 'Sao Paulo', 22000000),
(14, 7, 'Rio de Janeiro', 13400000),
(15, 8, 'London', 9300000),
(16, 8, 'Manchester', 2800000),
(17, 9, 'Paris', 11000000),
(18, 9, 'Lyon', 2300000),
(19, 10, 'Jakarta', 34500000),
(20, 10, 'Surabaya', 9000000);

INSERT INTO Polusi (id_polusi, id_negara, id_kota, tahun, indeks_kualitas_udara, indeks_karbon, indeks_ozon, indeks_nitrogen_dioksida) VALUES
(1,1,1,2018,42,58,33,29),
(2,1,1,2019,40,55,31,27),
(3,1,2,2020,48,63,35,34),
(4,1,2,2021,45,60,34,32),
(5,2,3,2019,30,41,22,18),
(6,2,3,2020,28,39,21,17),
(7,2,4,2021,33,45,25,20),
(8,2,4,2022,35,47,26,21),
(9,3,5,2018,25,35,18,16),
(10,3,5,2019,27,37,19,17),
(11,3,6,2020,29,38,20,18),
(12,3,6,2021,31,40,22,19),
(13,4,7,2019,52,65,38,42),
(14,4,7,2020,50,63,37,40),
(15,4,8,2021,58,70,41,45),
(16,4,8,2022,55,67,40,43),
(17,5,9,2018,20,28,15,10),
(18,5,9,2019,22,30,16,12),
(19,5,10,2020,24,31,17,13),
(20,5,10,2021,26,33,18,14),
(21,6,11,2018,78,92,55,60),
(22,6,11,2019,80,95,57,63),
(23,6,12,2020,85,100,60,68),
(24,6,12,2021,88,104,62,70),
(25,7,13,2019,67,80,45,50),
(26,7,13,2020,69,82,46,52),
(27,7,14,2021,72,85,49,55),
(28,7,14,2022,74,87,50,57),
(29,8,15,2018,33,48,28,24),
(30,8,15,2019,35,50,29,25),
(31,8,16,2020,37,53,30,27),
(32,8,16,2021,38,54,31,28),
(33,9,17,2019,40,55,32,30),
(34,9,18,2020,42,58,33,31),
(35,10,19,2021,85,110,60,72);

INSERT INTO KualitasHidup (id_kualitas_hidup, id_negara, tahun, indeks_kualitas_hidup, indeks_keamanan, indeks_kesehatan, indeks_pendidikan, indeks_biaya_hidup) VALUES
(1,1,2018,160,70,75,80,110),
(2,1,2019,162,72,76,81,112),
(3,1,2020,158,68,74,82,108),
(4,2,2019,175,80,82,85,95),
(5,2,2020,178,82,83,87,97),
(6,2,2021,180,84,85,88,98),
(7,3,2018,170,75,80,86,90),
(8,3,2019,172,76,81,87,92),
(9,3,2020,169,74,79,85,89),
(10,4,2019,150,65,78,90,105),
(11,4,2020,152,66,79,91,107),
(12,4,2021,154,67,80,92,108),
(13,5,2018,185,85,88,90,115),
(14,5,2019,188,87,89,92,118),
(15,5,2020,186,86,88,91,116),
(16,6,2018,110,50,60,65,55),
(17,6,2019,112,52,62,66,57),
(18,6,2020,115,54,63,67,60),
(19,6,2021,118,55,64,68,62),
(20,7,2018,120,55,65,70,65),
(21,7,2019,122,56,66,71,67),
(22,7,2020,125,57,67,72,69),
(23,7,2021,127,58,68,73,70),
(24,8,2018,165,78,80,88,102),
(25,8,2019,167,79,81,89,104),
(26,8,2020,170,80,82,90,106),
(27,9,2019,168,77,83,87,103),
(28,9,2020,170,78,84,88,105),
(29,9,2021,172,79,85,89,107),
(30,10,2018,130,60,70,75,50),
(31,10,2019,132,61,71,76,52),
(32,10,2020,135,62,73,77,55),
(33,10,2021,138,63,74,78,57),
(34,10,2022,140,64,75,80,59),
(35,10,2023,142,65,76,81,60);