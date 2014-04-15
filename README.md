ccasc-yaml
==========

Genellikle otomasyon işleri şöyle yapılır: İşi bilen kişi yapılacak işi (prosesi) anlatır, programcı hangi dilde ve hangi platformda gerekiyorsa programı yazar, operatör gerektiğinde parametreleri değiştirebilsin diye ekrana kutucuklar koyar. Böylece mesela bir yürüyen merdiven otomasyonu yapılmışsa ve "merdivende kimse yoksa 5 saniye sonra dur" denmişse, bunu 10 saniye yapmak için tekrar programcıya gidilmemiş olur.

Bu güne kadar yaptığım işler hep böyleydi.

Şimdi algoritmaya müşterinin karar vermesi gerekliliği oluştu. Belki pompa-1'den sonra 5 saniye bekleyip pompa-2'yi 10 saniye çalıştırmayacak da, pompa-1'den sonra pompa-3'ü 2 saniye çalıştırıp ardından pompa-1'i tekrar çalıştırıp, 3 saniye sonra durduracak. Fakat bu arada pompa-3 çalışmaya başladıktan 1 saniye sonra pompa-5'in çalışması da istenebilir. 

Mevzu fena karıştı.

Bu problemi çözebilecek en yakın sistem State Chart XML (SCXML) idi. Fakat XML fazla kriptik bir şey olduğu için bu amaca uymuyordu. Müşteriye Python öğretirdim, daha iyiydi. 

Mecburen yeni bir dil yapmaya karar verdim. 

Kısıtlar şöyleydi: 

1. Türkçe'deki düz yazı yazımına mümkün olduğunca yakın olacak.
2. Mümkün olduğunca az özel işaret kullanılacak.

Mesela bu dille (cca-scyaml) bir yürüyen merdiven otomasyonu yapalım:

    - Sistem çalışıyor:
        - Merdivenin başında nesne var -> Merdiven çalış, 1 tur + 5 sn

Bu kadar. 


Burada "Sistem" adında bir nesne var, "çalışıyor" ise altında girintilenmiş işleri yapıyor. Bir diğer nesne "Merdivenin başında nesne" isimli dedektör. Eğer "var" diyorsa sıradaki işe geçilir. Sıradaki işin nesnesinin adı "Merdiven", buna "çalış" sinyalini gönderiyoruz, parametre olarak da "1 tur + 5 sn" veriyoruz.


Derleyici özel kelimeleri yakalıyor, yapılacakları bu kelimelere göre planlıyor. Kullanıcı bu özel kelimeleri bilmek zorunda. 
