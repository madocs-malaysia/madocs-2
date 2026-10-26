/* MADOCS 2.0 — skrip laman */
(function () {
  "use strict";

  /* ---- bahasa: halaman Inggeris berada di bawah /en/ ---- */
  var EN = document.documentElement.lang === "en";
  var JEJAK_CARIAN = EN ? "/en/search" : "/carian";
  var TEKS = EN ? {
    minimum: "Type at least 2 characters to start searching.",
    hasil: "results found for",
    tiada: "No results",
    cuba: "Try another keyword, or contact the MADOCS secretariat for help.",
    buka: "Open",
    gagal: "The search index could not be loaded."
  } : {
    minimum: "Taip sekurang-kurangnya 2 aksara untuk mula mencari.",
    hasil: "hasil dijumpai untuk",
    tiada: "Tiada hasil",
    cuba: "Cuba kata kunci lain, atau hubungi urusetia MADOCS untuk bantuan.",
    buka: "Buka",
    gagal: "Indeks carian tidak dapat dimuatkan."
  };

  /* ---- menu mudah alih ---- */
  var butangMenu = document.querySelector(".menu-toggle");
  var menu = document.getElementById("menu-mudah");
  if (butangMenu && menu) {
    butangMenu.addEventListener("click", function () {
      var buka = menu.hasAttribute("hidden");
      if (buka) { menu.removeAttribute("hidden"); } else { menu.setAttribute("hidden", ""); }
      butangMenu.setAttribute("aria-expanded", buka ? "true" : "false");
    });
  }

  /* ---- anak panah carousel aktiviti ---- */
  var grid = document.querySelector(".activity-grid");
  var anak = document.querySelectorAll(".carousel-arrow");
  if (grid && anak.length) {
    var bolehSkrol = grid.scrollWidth > grid.clientWidth + 4;
    grid.style.overflowX = "auto";
    grid.style.scrollSnapType = "x mandatory";
    Array.prototype.forEach.call(grid.children, function (c) { c.style.scrollSnapAlign = "start"; });
    if (!bolehSkrol) {
      Array.prototype.forEach.call(anak, function (b) { b.style.display = "none"; });
    } else {
      anak.forEach(function (b) {
        b.addEventListener("click", function () {
          var arah = b.classList.contains("left") ? -1 : 1;
          grid.scrollBy({ left: arah * grid.clientWidth * 0.8, behavior: "smooth" });
        });
      });
    }
  }

  /* ---- carian pantas di laman utama ---- */
  var pantas = document.getElementById("carian-pantas");
  var butang = document.getElementById("butang-carian");
  function pergiCarian() {
    if (!pantas || !pantas.value.trim()) { return; }
    window.location.href = JEJAK_CARIAN + "/?q=" + encodeURIComponent(pantas.value.trim());
  }
  if (pantas) {
    pantas.addEventListener("keydown", function (e) { if (e.key === "Enter") { pergiCarian(); } });
  }
  if (butang && pantas) {
    butang.addEventListener("click", function (e) { e.preventDefault(); pergiCarian(); });
  }

  /* ---- halaman carian ---- */
  var medan = document.getElementById("medan-carian");
  if (medan) {
    var info = document.getElementById("hasil-info");
    var senarai = document.getElementById("hasil-senarai");
    var indeks = null;

    function sorot(teks, kata) {
      if (!kata || !teks) { return teks || ""; }
      var i = teks.toLowerCase().indexOf(kata.toLowerCase());
      if (i < 0) { return teks; }
      return teks.slice(0, i) + "<mark>" + teks.slice(i, i + kata.length) + "</mark>" + teks.slice(i + kata.length);
    }

    function papar(kata) {
      var hasil = [];
      if (kata.length >= 2 && indeks) {
        var k = kata.toLowerCase();
        hasil = indeks.filter(function (it) {
          return (it.t + " " + (it.r || "") + " " + (it.j || "")).toLowerCase().indexOf(k) >= 0;
        });
      }
      if (kata.length < 2) {
        info.textContent = TEKS.minimum;
        senarai.innerHTML = "";
        return;
      }
      info.textContent = hasil.length + " " + TEKS.hasil + " \"" + kata + "\".";
      if (!hasil.length) {
        senarai.innerHTML = '<div class="kosong"><h3>' + TEKS.tiada + '</h3><p>' + TEKS.cuba + '</p></div>';
        return;
      }
      senarai.innerHTML = hasil.map(function (it) {
        return '<article class="item no-photo"><div class="item-body">' +
          '<span class="badge">' + it.j + "</span>" +
          '<h3><a href="' + it.u + '">' + sorot(it.t, kata) + "</a></h3>" +
          '<p>' + sorot(it.r || "", kata) + "</p>" +
          '<a class="lebih" href="' + it.u + '">' + TEKS.buka + "</a></div></article>";
      }).join("");
    }

    var q = new URLSearchParams(window.location.search).get("q") || "";
    fetch(JEJAK_CARIAN + "/index.json")
      .then(function (r) { return r.json(); })
      .then(function (j) { indeks = j; if (q) { medan.value = q; papar(q); } else { papar(""); } })
      .catch(function () { info.textContent = TEKS.gagal; });

    medan.addEventListener("input", function () { papar(medan.value.trim()); });
  }

  /* ---- pengepala mengecil selepas skrol ---- */
  var pengepala = document.querySelector(".header");
  if (pengepala) {
    var tandaKompak = function () {
      if (window.scrollY > 40) { pengepala.classList.add("kompak"); }
      else { pengepala.classList.remove("kompak"); }
    };
    tandaKompak();
    window.addEventListener("scroll", tandaKompak, { passive: true });
  }

  /* ---- kemunculan lembut semasa skrol ----
     Kelas .mula ditambah oleh JS sahaja: jika JS gagal atau pengguna minta kurang
     gerakan, kandungan kekal kelihatan (tiada risiko halaman kosong). */
  var kurangGerak = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!kurangGerak && "IntersectionObserver" in window) {
    var blok = document.querySelectorAll(
      ".section-pad > .shell > *, .page-hero > .shell > *, .course-feature, .activity-card, .item, .card, .content-wrap > .shell > *");
    if (blok.length) {
      var pemerhati = new IntersectionObserver(function (masuk) {
        masuk.forEach(function (satu) {
          if (!satu.isIntersecting) { return; }
          satu.target.classList.add("muncul");
          pemerhati.unobserve(satu.target);
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
      Array.prototype.forEach.call(blok, function (el, i) {
        el.classList.add("mula");
        el.style.transitionDelay = (Math.min(i % 4, 3) * 45) + "ms";
        pemerhati.observe(el);
      });

      /* Keselamatan: IntersectionObserver boleh terlepas elemen bila pelawat melompat
         atau skrol terlalu laju (kes sebenar: kandungan kekal halimunan). Sapu elemen
         yang berada dalam paparan tetapi masih belum muncul, dan buka semuanya selepas
         beberapa saat supaya tiada kandungan tersembunyi selama-lamanya. */
      function sapu() {
        Array.prototype.forEach.call(document.querySelectorAll(".mula:not(.muncul)"), function (el) {
          var b = el.getBoundingClientRect();
          if (b.top < window.innerHeight && b.bottom > 0) { el.classList.add("muncul"); }
        });
      }
      sapu();
      window.addEventListener("scroll", function () { window.requestAnimationFrame(sapu); }, { passive: true });
      window.addEventListener("resize", sapu, { passive: true });
      window.setTimeout(function () {
        Array.prototype.forEach.call(document.querySelectorAll(".mula"), function (el) {
          el.classList.add("muncul");
        });
      }, 4000);
    }
  }
})();

/* ---- MADOCS 2.0: lightbox galeri ----
   Thumbnail galeri ialah <button> supaya boleh dicapai papan kekunci. Klik atau Enter
   membuka lapisan penuh; Esc menutup, anak panah kiri/kanan menukar gambar. */
(function () {
  "use strict";
  var EN = document.documentElement.lang === "en";
  var TEKS = EN ? { tutup: "Close", sebelum: "Previous photo", selepas: "Next photo" }
                : { tutup: "Tutup", sebelum: "Gambar sebelum", selepas: "Gambar seterusnya" };
  var senarai = Array.prototype.slice.call(document.querySelectorAll(".gambar[data-besar]"));
  if (!senarai.length) { return; }

  var kotak = document.createElement("div");
  kotak.className = "lightbox";
  kotak.setAttribute("role", "dialog");
  kotak.setAttribute("aria-modal", "true");
  kotak.hidden = true;
  kotak.innerHTML =
    '<button class="lb-tutup" type="button" aria-label="' + TEKS.tutup + '">\u00d7</button>' +
    '<button class="lb-sebelum" type="button" aria-label="' + TEKS.sebelum + '">\u2039</button>' +
    '<img alt="">' +
    '<p class="lb-kapsyen"></p>' +
    '<button class="lb-selepas" type="button" aria-label="' + TEKS.selepas + '">\u203a</button>';
  document.body.appendChild(kotak);

  var imej = kotak.querySelector("img");
  var kapsyen = kotak.querySelector(".lb-kapsyen");
  var indeks = 0;
  var fokus_asal = null;
  var adaSebelum = senarai.length > 1;
  kotak.querySelector(".lb-sebelum").hidden = !adaSebelum;
  kotak.querySelector(".lb-selepas").hidden = !adaSebelum;

  function tunjuk(i) {
    indeks = (i + senarai.length) % senarai.length;
    var butang = senarai[indeks];
    imej.src = butang.getAttribute("data-besar");
    imej.alt = butang.getAttribute("data-kapsyen") || "";
    kapsyen.textContent = butang.getAttribute("data-kapsyen") || "";
  }

  function buka(i) {
    fokus_asal = document.activeElement;
    tunjuk(i);
    kotak.hidden = false;
    document.body.style.overflow = "hidden";
    kotak.querySelector(".lb-tutup").focus();
  }

  function tutup() {
    kotak.hidden = true;
    imej.src = "";
    document.body.style.overflow = "";
    if (fokus_asal && fokus_asal.focus) { fokus_asal.focus(); }
  }

  senarai.forEach(function (butang, i) {
    butang.addEventListener("click", function () { buka(i); });
  });
  kotak.querySelector(".lb-tutup").addEventListener("click", tutup);
  kotak.querySelector(".lb-sebelum").addEventListener("click", function () { tunjuk(indeks - 1); });
  kotak.querySelector(".lb-selepas").addEventListener("click", function () { tunjuk(indeks + 1); });
  kotak.addEventListener("click", function (e) { if (e.target === kotak) { tutup(); } });
  document.addEventListener("keydown", function (e) {
    if (kotak.hidden) { return; }
    if (e.key === "Escape") { tutup(); }
    else if (e.key === "ArrowLeft") { tunjuk(indeks - 1); }
    else if (e.key === "ArrowRight") { tunjuk(indeks + 1); }
  });
})();

  /* ---- roulette imej hero ----
     Slaid pertama dimuatkan segera; slaid lain dimuatkan selepas halaman sedia (data-src).
     Putaran berhenti bila pengguna minta kurang gerakan, tab tidak aktif, atau tetikus
     berada di atas hero. Tanpa JS, slaid pertama kekal kelihatan. */
  (function () {
    var slaid = Array.prototype.slice.call(document.querySelectorAll(".hero-slaid"));
    if (slaid.length < 2) { return; }
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) { return; }

    var hero = document.querySelector(".hero");
    var selang = ((parseInt(hero && hero.getAttribute("data-selang"), 10) || 7)) * 1000;
    var indeks = 0, pemasa = null;

    function muatSemua() {
      slaid.forEach(function (p) {
        var s = p.querySelector("source[data-srcset]");
        var i = p.querySelector("img[data-src]");
        if (s) { s.srcset = s.getAttribute("data-srcset"); s.removeAttribute("data-srcset"); }
        if (i) { i.src = i.getAttribute("data-src"); i.removeAttribute("data-src"); }
      });
    }
    function tukar() {
      slaid[indeks].classList.remove("aktif");
      indeks = (indeks + 1) % slaid.length;
      slaid[indeks].classList.add("aktif");
      tandaTitik();
    }
    function pergi(arah) {
      slaid[indeks].classList.remove("aktif");
      indeks = (indeks + arah + slaid.length) % slaid.length;
      slaid[indeks].classList.add("aktif");
      tandaTitik();
    }
    function mula() { if (!pemasa) { pemasa = window.setInterval(tukar, selang); } }
    function henti() { if (pemasa) { window.clearInterval(pemasa); pemasa = null; } }
    function tolak(arah) { pergi(arah); henti(); mula(); }

    /* --- anak panah: pengguna desktop tiada swipe --- */
    var titik = [];
    function tandaTitik() {
      for (var i = 0; i < titik.length; i++) {
        titik[i].setAttribute("aria-current", i === indeks ? "true" : "false");
      }
    }
    if (hero) {
      /* Satu baris kawalan: < · · · · · > (anak panah dan titik sebaris) */
      var kawalan = document.createElement("div");
      kawalan.className = "hero-kawalan";
      hero.appendChild(kawalan);
      var butang = [
        { kelas: "hero-nav-kiri", arah: -1, label: "Slaid sebelum", ikon: "M15 18l-6-6 6-6" },
        { kelas: "hero-nav-kanan", arah: 1, label: "Slaid seterusnya", ikon: "M9 18l6-6-6-6" },
      ];
      butang.forEach(function (b) {
        var el = document.createElement("button");
        el.type = "button";
        el.className = "hero-nav " + b.kelas;
        el.setAttribute("aria-label", b.label);
        el.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" ' +
                       'stroke-linejoin="round" stroke-width="2" aria-hidden="true"><path d="' + b.ikon + '"/></svg>';
        el.addEventListener("click", function (e) { e.preventDefault(); tolak(b.arah); });
        kawalan.appendChild(el);
      });

      /* --- titik penunjuk di sisi kanan gambar --- */
      var bekasTitik = document.createElement("div");
      bekasTitik.className = "hero-titik";
      bekasTitik.setAttribute("role", "tablist");
      bekasTitik.setAttribute("aria-label", "Pilih slaid");
      slaid.forEach(function (s, i) {
        var t = document.createElement("button");
        t.type = "button";
        t.setAttribute("aria-label", "Slaid " + (i + 1));
        t.addEventListener("click", function (e) {
          e.preventDefault();
          slaid[indeks].classList.remove("aktif");
          indeks = i;
          slaid[indeks].classList.add("aktif");
          tandaTitik(); henti(); mula();
        });
        bekasTitik.appendChild(t);
        titik.push(t);
      });
      kawalan.insertBefore(bekasTitik, kawalan.querySelector(".hero-nav-kanan"));
      tandaTitik();
    }

    /* --- swipe kiri/kanan pada skrin sentuh --- */
    if (hero) {
      var x0 = null, y0 = null, menegak = false;
      hero.addEventListener("touchstart", function (e) {
        if (!e.touches || e.touches.length !== 1) { return; }
        x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; menegak = false;
      }, { passive: true });
      hero.addEventListener("touchmove", function (e) {
        if (x0 === null || !e.touches || e.touches.length !== 1) { return; }
        var dx = e.touches[0].clientX - x0, dy = e.touches[0].clientY - y0;
        if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > 14) { menegak = true; }
      }, { passive: true });
      hero.addEventListener("touchend", function (e) {
        if (x0 === null) { return; }
        var t = (e.changedTouches && e.changedTouches[0]) || null;
        if (t && !menegak) {
          var dx = t.clientX - x0;
          if (Math.abs(dx) > 45) { tolak(dx < 0 ? 1 : -1); }
        }
        x0 = null; y0 = null;
      }, { passive: true });
      /* hentikan putaran automatik sementara jari menyentuh hero */
      hero.addEventListener("touchstart", henti, { passive: true });
      hero.addEventListener("touchend", mula, { passive: true });
    }

    window.setTimeout(function () { muatSemua(); mula(); }, 2500);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) { henti(); } else { mula(); }
    });
    if (hero) {
      hero.addEventListener("mouseenter", henti);
      hero.addEventListener("mouseleave", mula);
      hero.addEventListener("focusin", henti);
      hero.addEventListener("focusout", mula);
    }
  })();

/* ---- MADOCS 2.0: pengesahan sijil C&P ----
   Membaca indeks awam yang tertanam dalam halaman (tiada nama/nombor MMC disimpan). */
(function () {
  "use strict";
  var el = document.getElementById("indeks-sijil");
  var borang = document.getElementById("borang-sahkan");
  if (!el || !borang) { return; }

  var indeks = [];
  try { indeks = (JSON.parse(el.textContent || "{}").sijil) || []; } catch (e) { indeks = []; }

  var EN = document.documentElement.lang === "en";
  var T = EN
    ? { jaya: "Certificate is valid", gagal: "Not found", kursus: "Course", tarikh: "Date",
        cpd: "CPD points", hash: "SHA-256 (first 32 characters)", siri: "Serial number",
        batal: "This certificate has been revoked." }
    : { jaya: "Sijil ini sah", gagal: "Tidak dijumpai", kursus: "Kursus", tarikh: "Tarikh",
        cpd: "Mata CPD", hash: "SHA-256 (32 aksara pertama)", siri: "Nombor siri",
        batal: "Sijil ini telah dibatalkan." };

  var masuk = document.getElementById("siri");
  var hasil = document.getElementById("hasil-sahkan");

  function tunjuk(html, kelas) {
    hasil.className = "hasil-sahkan " + (kelas || "");
    hasil.innerHTML = html;
  }

  function cari(siri) {
    var kunci = String(siri || "").trim().toUpperCase();
    if (!kunci) { return null; }
    for (var i = 0; i < indeks.length; i++) {
      if (String(indeks[i].siri || "").toUpperCase() === kunci) { return indeks[i]; }
    }
    return null;
  }

  function papar(siri) {
    var r = cari(siri);
    var kunci = String(siri || "").trim();
    if (!r) {
      tunjuk("<h3>" + T.gagal + "</h3><p>" + (EN ? "No certificate with serial number " : "Tiada sijil dengan nombor siri ")
             + "<b>" + kunci.replace(/[<>&]/g, "") + "</b> "
             + (EN ? "is recorded by MADOCS. Please check the number on the certificate and try again."
                   : "dalam rekod MADOCS. Sila semak semula nombor pada sijil atau hubungi urusetia.") + "</p>", "gagal");
      return;
    }
    if (r.status && r.status !== "sah") {
      tunjuk("<h3>" + T.batal + "</h3><p>" + (r.nota || "") + "</p>", "gagal");
      return;
    }
    var baris = [
      [T.siri, r.siri], [T.kursus, (r.kod ? r.kod + " — " : "") + (r.kursus || "")],
      [T.tarikh, r.tarikh || ""], [T.cpd, r.cpd || ""], [T.hash, r.hash || ""]
    ];
    tunjuk('<h3>' + T.jaya + '</h3><dl class="senarai-sah">'
           + baris.map(function (b) {
               return '<div><dt>' + b[0] + '</dt><dd>' + String(b[1] == null ? '' : b[1]).replace(/[<>&]/g, '') + '</dd></div>';
             }).join('')
           + '</dl><p class="nota-isi">'
           + (EN ? "Match the serial number and hash with the certificate you received. Names and MMC numbers are not stored in this public record."
                 : "Padankan nombor siri dan hash dengan sijil yang diterima. Nama dan nombor MMC tidak disimpan dalam rekod awam ini.")
           + "</p>", "jaya");
  }

  borang.addEventListener("submit", function (e) { e.preventDefault(); papar(masuk.value); });

  var q = null;
  try { q = new URLSearchParams(window.location.search).get("s"); } catch (e) { q = null; }
  if (q) { masuk.value = q; papar(q); }
})();

/* --- Pengesahan status ahli (/semak-ahli/) --- */
(function () {
  var el = document.getElementById("indeks-ahli");
  var borang = document.getElementById("borang-ahli");
  if (!el || !borang) { return; }

  var indeks = [];
  try { indeks = (JSON.parse(el.textContent || "{}").ahli) || []; } catch (e) { indeks = []; }

  var EN = document.documentElement.lang === "en";
  var T = EN
    ? { jaya: "Active member", tamat: "Membership expired", tangguh: "Membership suspended",
        gagal: "Not found", no: "Member number", nama: "Name", kategori: "Category",
        status: "Status", sah: "Valid until", seumur: "Lifetime membership — no expiry",
        tiadaSah: "Not recorded — ask the secretariat",
        aktif: "Active", ditamat: "Expired", ditangguh: "Suspended" }
    : { jaya: "Ahli aktif", tamat: "Keahlian telah tamat", tangguh: "Keahlian ditangguh",
        gagal: "Tidak dijumpai", no: "Nombor ahli", nama: "Nama", kategori: "Kategori",
        status: "Status", sah: "Sah hingga", seumur: "Keahlian seumur hidup — tiada tarikh luput",
        tiadaSah: "Tidak direkodkan — sila tanya urusetia",
        aktif: "Aktif", ditamat: "Tamat tempoh", ditangguh: "Ditangguh" };

  var masuk = document.getElementById("no-ahli");
  var hasil = document.getElementById("hasil-ahli");

  function tunjuk(html, kelas) {
    hasil.className = "hasil-sahkan " + (kelas || "");
    hasil.innerHTML = html;
  }

  function cari(no) {
    var kunci = String(no || "").trim().toUpperCase().replace(/[^A-Z0-9]/g, "");
    if (!kunci) { return null; }
    for (var i = 0; i < indeks.length; i++) {
      if (String(indeks[i].no || "").toUpperCase().replace(/[^A-Z0-9]/g, "") === kunci) { return indeks[i]; }
    }
    return null;
  }

  function baris(label, nilai) {
    return '<div><dt>' + label + '</dt><dd>' + String(nilai == null ? "" : nilai).replace(/[<>&]/g, "") + '</dd></div>';
  }

  function papar(no) {
    var r = cari(no);
    var kunci = String(no || "").trim().replace(/[<>&]/g, "");
    if (!r) {
      tunjuk("<h3>" + T.gagal + "</h3><p>" + (EN ? "No member with number " : "Tiada ahli dengan nombor ")
             + "<b>" + kunci + "</b> " + (EN ? "is recorded by MADOCS. Please check the number on the membership certificate."
                                             : "dalam rekod MADOCS. Sila semak semula nombor pada sijil keahlian.") + "</p>", "gagal");
      return;
    }
    var status = String(r.status || "").toLowerCase();
    var labelStatus = status === "aktif" ? T.aktif : (status === "tamat" ? T.ditamat : T.ditangguh);
    var sah;
    if (r.sah_hingga) { sah = r.sah_hingga; }
    else if (/seumur/i.test(String(r.kategori || ""))) { sah = T.seumur; }
    else { sah = T.tiadaSah; }
    var dl = '<dl class="senarai-sah">'
      + baris(T.no, r.no) + baris(T.nama, r.nama_papar) + baris(T.kategori, r.kategori)
      + baris(T.status, labelStatus) + baris(T.sah, sah) + '</dl>';

    if (status === "aktif") {
      tunjuk("<h3>" + T.jaya + "</h3>" + dl + '<p class="nota-isi">'
             + (EN ? "This record shows membership status only. Identity card and MMC numbers are not stored here."
                   : "Rekod ini hanya menunjukkan status keahlian. Nombor kad pengenalan dan MMC tidak disimpan di sini.")
             + "</p>", "jaya");
    } else if (status === "tamat") {
      tunjuk("<h3>" + T.tamat + "</h3>" + dl + '<p class="nota-isi">'
             + (EN ? "Please ask the member to renew before relying on this membership."
                   : "Sila minta ahli memperbaharui keahlian sebelum bergantung pada status ini.")
             + "</p>", "gagal");
    } else {
      tunjuk("<h3>" + T.tangguh + "</h3>" + dl + '<p class="nota-isi">'
             + (EN ? "Contact the MADOCS secretariat for the reason and current standing."
                   : "Hubungi urusetia MADOCS untuk sebab dan kedudukan semasa.")
             + "</p>", "gagal");
    }
  }

  borang.addEventListener("submit", function (e) { e.preventDefault(); papar(masuk.value); });

  var q = null;
  try { q = new URLSearchParams(window.location.search).get("a"); } catch (e) { q = null; }
  if (q) { masuk.value = q; papar(q); }
})();
