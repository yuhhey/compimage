#!/bin/bash

# sed - et használom múltbeli archiválási hibák kiküszöbölésére

./create_file_list.sh ./* | sed '
/Thumbs.db/d
/checksum/d
/ZbThumb/d
s/ //g
s/^Kina/JPG\/Kina/

# VEGYES_2 valójában HG10-es diszk. Hozzáadjuk a HG10-es előtagot.
s/^200902/HG10\/200902/

# 20090930-én írtam DVD-t, de nem töröltem le a HG10-ről, ezért a 20091002-es
# direktoriban van a disken. Lusta voltam újra írni a már meglévő MTS fájlokat
# A kísérő fájlok (thumbnails, CPI és barátaik) duplán vannak mentve,
# ezért itt csak az MTS-ek elérését módosítom
# Közben a dátumformátumot is megváltoztattam
s/20090930\/BDMV\/STREAM\/000/2009_10_02\/BDMV\/STREAM\/000/

# Nem emlékszem miért a HG10/2009_10_06 a dvd-n HG10/2009_10_05
s/HG10\/2009_10_05/HG10\/2009_10_06/

# Elgépeltem a direktori nevét, a vinyóm kijavítottam, de újra írni nem fogom.
s/Ausztalia/Ausztralia/

# Néhány szabály, ami a <space>-ek eltüntetése miatt kell. A DVD-n van <space>
# és a szavak kisbetűvel vannak: "Szo1 szo2" -> "Szo1Szo2"
s/Amerika\/utaz/Amerika\/Utaz/
s/Hargitatura/HargitaTura/
s/2005erdely/2005Erdely/
s/Puchnerkastely/PuchnerKastely/
s/Kolibriformarovar/KolibriFormaRovar/
s/Tejfolosgomba/TejfolosGomba/
s/Egeravarbol/EgerAVarbol/g

# Ékezeteket is lecseréltem a fájlnevekben.
y/,űáéúőóüöíŰÁÉÚŐÓÜÖÍ/-uaeuoouoiUAEUOOUOI/

# Töröljük a speciális karaktereket
s/!//
s/&/Es/

# néhány fájlnevet az ékezetes betűk cseréje után egyszerűbb módosítani
s/fustolojr/Fustoloje/
s/KaracsonyesSzilveszter/KaracsonyEsSzilveszter/
s/0729-viragok/0729Viragok/
s/Bobbieknalunk/BobbiekNalunk/
s/Canonlencse/CanonLencse/
s/Tianfusoftwarepark/TianfuSoftwarePark/
s/TVahotelben/TVaHotelben/
s/Dunduliszuli/DunduliSzuli/
s/Faejjel/FaEjjel/
s/Feherasztal/FeherAsztal/
s/Kaktuszviragzik/KaktuszViragzik/
s/Kina2\.latogatas\/PekingChengdur/KinaMasodikLatogatas\/PekingChengduR/
s/Kina2\.latogatas\/ShangriLas/KinaMasodikLatogatas\/ShangriLaS/
s/Nyuszofejen/NyuszoFejen/
s/Sanyibacsi/SanyiBacsi/
s/Sigmalencse/SigmaLencse/
s/kurautan/KuraUtan/
s/anyci/Anyci/
s/16\.emeletilakas/16EmeletiLakas/
s/Szkopab/SzkopAb/
s/Skacokb/SkacokB/
s/Zizibuli/ZiziBuli/
s/Erdelylovas/ErdelyLovas/
s/cspat/csapat/
s/DettiEsPoplacsek/DettiPoplacsek/
s/dettiEspoplacsek/dettipoplacsek/
' | sort | uniq> fajllista_dvdn
