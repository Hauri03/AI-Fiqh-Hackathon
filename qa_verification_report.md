# Q&A Verification Report

This document provides the "Source of Truth" for the 30 Q&A pairs generated in `rag_eval_qa_pairs.json`. Use this to verify that the answers are grounded in the original documents.

## 1. Mufti Selangor (5 Pairs)
**Source File**: `filtered_finance_questions.json`

| Index | Question | Answer Source Snippet (Verification) |
| :--- | :--- | :--- |
| 1 | Forex Trading | *"Muzakarah Jawatankuasa Fatwa Majlis Kebangsaan... memutuskan bahawa perdagangan pertukaran mata wang asing (forex) oleh individu secara lani... adalah haram..."* (Fatwa Online) |
| 2 | Apartment Late Charges | *"Pihak pengurusan boleh mengenakan caj denda ke atas penghuni yang lewat membayar kos penyelenggaraan... Ia dianggap sebagai ta'widh (ganti rugi)..."* |
| 3 | ASB Investment | *"Hukum pelaburan PNB dalam ASNB adalah harus kerana peratusan pelaburan saham syarikat patuh syarak telah melepasi 66%..."* |
| 4 | Conventional Bus Insurance | *"Hukumnya tidak berdosa dan tidak haram saudara menaiki bas tersebut... insuran tersebut adalah diambil oleh pihak pengurusan bas dan ianya adalah tanggungjawab syarikat..."* |
| 5 | Trading Without License | *"Pendapatan yang diperolehi hasil jualan tersebut adalah halal dan sah... Namun begitu, perbuatan berniaga tanpa permit adalah menyalahi undang-undang..."* |

## 2. Mufti Wilayah Persekutuan (5 Pairs)
**Source File**: `mufti_wp_finance_candidates.json`

| Index | Question | Answer Source Snippet (Verification) |
| :--- | :--- | :--- |
| 6 | Gold Bar Shopee | *"Haram dan tidak sah kerana berlaku penangguhan serahan... Syarat sah jual beli emas dengan wang ialah serahan serta-merta (yadan bi yadin)..."* (Irsyad Hukum Siri Ke-943) |
| 7 | Zafar bi al-Haq (Taking Debt Secretly) | *"Dibenarkan (Harus) dengan syarat: 1) Telah mencuba pelbagai cara lain... 2) Tidak mengambil melebihi kadar haknya..."* (Irsyad Hukum Siri Ke-743) |
| 8 | Transaction by Children | *"Hukum jual beli kanak-kanak adalah tidak sah kecuali bagi barangan yang kecil dan ringan... Bagi barangan bernilai tinggi, ia memerlukan keizinan..."* (Irsyad Hukum Siri Ke-741) |
| 9 | Bribery in Desperation | *"Hukum asal rasuah adalah haram mutlak... sebahagian ulama memberikan pengecualian... jika ia satu-satunya jalan untuk mendapatkan hak..."* (Irsyad Hukum Siri Ke-740) |
| 10 | Khairat Kematian vs Faraid | *"Wang khairat kematian adalah sumbangan (tabarru')... Lebihan wang... adalah hak milik ahli keluarga yang menanggung perbelanjaan... bukan harta pusaka..."* |

## 3. MPS BNM Shariah Resolutions (20 Pairs)
**Source File**: `all_chapters_content.txt` (Extracted from PDF Chapters)

### Chapter: Bai' Al-Sarf
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 11 | T+2 Settlement | *"Amalan serah terima mata wang dalam bai` al-sarf, contohnya yang dilaksanakan pada hari kedua... boleh dibenarkan berdasarkan amalan pasaran (`urf tijari) ekoran daripada kekangan operasi."* (Section 27) |
| 12 | Payment in Different Currency | *"MPS... memutuskan bahawa pembayaran hutang dalam mata wang berbeza daripada mata wang hutang yang asal adalah diharuskan dengan syarat kadar pertukaran mata wang terlibat adalah kadar pertukaran pasaran pada hari pembayaran..."* (Section 28) |

### Chapter: Hibah
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 13 | Future Asset (Hibah) | *"Walau apa pun perkara (ii), aset yang akan diterima oleh pemberi hibah pada masa hadapan dibenarkan untuk dijadikan sebagai aset hibah."* (Section 29) |
| 14 | Revocation by Father | *"MPS... memutuskan bahawa hibah daripada seorang bapa kepada anaknya boleh ditarik balik kecuali... Sekiranya pemilikan aset hibah telah dipindahkan kepada pihak ketiga; atau Aset hibah dicagarkan."* (Section 33) |

### Chapter: Ijarah
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 15 | Takaful Cost Liability | *"MPS... memutuskan bahawa dalam pembiayaan kenderaan yang berasaskan kontrak sewa beli Islam, kos takaful boleh ditanggung oleh penyewa..."* (Section 35) |
| 16 | Floating Rate Limits | *"MPS... memutuskan bahawa amalan kadar sewaan boleh ubah dalam kontrak ijarah mestilah mempunyai penetapan had minimum dan maksimum."* (Section 38) |

### Chapter: Istisna
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 17 | Penalty for Delay (Syart Jaza'i) | *"MPS... memutuskan bahawa semasa pemeteraian kontrak istisna`, pihak yang berkontrak boleh bersetuju dengan pengenaan syart jaza’i ke atas sani` dalam kes kelewatan..."* (Section 42) |
| 18 | Selling Before Possession | *"Mustasni` dalam kontrak istisna` tidak boleh menjual atau mencagarkan aset istisna` yang belum diserahkan hak milik kepadanya."* (Section 43) |

### Chapter: Kafalah
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 19 | Fee Liability | *"MPS... memutuskan bahawa fi kafalah boleh dikenakan ke atas mana-mana pihak yang mendapat manfaat daripada perkhidmatan kafalah..."* (Section 52) |
| 20 | Concurrent Claims | *"MPS telah memutuskan bahawa makful lahu boleh menuntut amaun hutang belum bayar daripada makful `anhu dan juga daripada harta peninggalan kafil secara serentak. ...dinasihatkan supaya memulakan tuntutan... terhadap makful `anhu terlebih dahulu..."* (Section 53) |

### Chapter: Qard
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 21 | Gift (Hibah) to Lender | *"Pemberian atau promosi manfaat secara kontraktual... dan diberikan secara eksklusif kepada pemberi qard adalah tidak dibenarkan. ...diberikan secara umum... adalah dibenarkan..."* (Section 54) |
| 22 | Incidental Qard (Mu'atah) | *"MPS... memutuskan bahawa kontrak qard secara insidental boleh dilakukan melalui kaedah mu`atah... tanpa memerlukan sebarang dokumentasi qard."* (Section 56) |

### Chapter: Rahn
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 23 | Mixed Assets Collateral | *"Aset bercampur boleh diterima sebagai cagaran dengan syarat... Nilai cagaran mestilah terhad kepada bahagian yang patuh Syariah sahaja."* (Section 58) |
| 24 | Usage by Pledgor | *"MPS... memutuskan bahawa rahin yang juga pemilik aset boleh menggunakan dan mengambil manfaat daripada marhun dengan izin murtahin."* (Section 60) |

### Chapter: Tawarruq
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 25 | Dual Agency | *"Dwi-agensi dalam tawarruq merujuk kepada tindakan suatu pihak menjadi wakil untuk membuat pembelian... dan setelah itu menjadi wakil... untuk menjual aset tersebut kepada dirinya sendiri... diaturkan dwi-agensi mestilah mempunyai bukti transaksi murabahah..."* (Section 66) |
| 26 | Hawalah Debt Transfer | *"MPS... memutuskan bahawa hawalah al-dayn memberi kesan penyelesaian hutang asal dalam kontrak jual beli bertangguh."* (Section 67) |

### Chapter: Wad
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 27 | Binding Promise | *"Wa`d adalah mengikat (mulzim) ke atas pemberi janji sekiranya janji tersebut dikaitkan dengan... Tindakan tertentu... Masa atau tarikh... Peristiwa atau situasi..."* (Section 68(a)) |
| 28 | Non-Shariah Subject | *"MPS... memutuskan bahawa subjek wa`d mestilah terhad kepada aktiviti/tindakan yang patuh Syariah."* (Section 69) |

### Chapter: Wakalah
| Index | Question | Verification Snippet from Text |
| :--- | :--- | :--- |
| 29 | Dual Representation | *"MPS... memutuskan bahawa pelantikan wakil yang sama... tidak dibenarkan, melainkan jika syarat-syarat berikut dipatuhi: i. Kriteria asas... ii. Transaksi... disokong oleh bukti... iii. Semua perjanjian wakalah... didedahkan..."* (Section 71) |
| 30 | Breach by Agent | *"MPS... memutuskan bahawa dalam kes pelanggaran syarat oleh wakil di bawah kontrak wakalah bi al-istithmar, wakil mestilah menjamin: i. modal pelaburan; dan ii. keuntungan sebenar..."* (Section 74) |
