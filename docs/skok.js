const KSIEGI = [{"kod": "01-gen", "klucz": "rdz"}, {"kod": "02-exo", "klucz": "wj"}, {"kod": "03-lev", "klucz": "kpł"}, {"kod": "04-num", "klucz": "lb"}, {"kod": "05-deu", "klucz": "pwt"}, {"kod": "06-jos", "klucz": "joz"}, {"kod": "07-jud", "klucz": "sdz"}, {"kod": "08-rut", "klucz": "rt"}, {"kod": "09-reg", "klucz": "1sm"}, {"kod": "10-reg", "klucz": "2sm"}, {"kod": "11-reg", "klucz": "1krl"}, {"kod": "12-reg", "klucz": "2krl"}, {"kod": "13-par", "klucz": "1krn"}, {"kod": "14-par", "klucz": "2krn"}, {"kod": "15-esd", "klucz": "ezd"}, {"kod": "16-esd", "klucz": "ne"}, {"kod": "17-est", "klucz": "est"}, {"kod": "18-iob", "klucz": "hi"}, {"kod": "19-psa", "klucz": "ps"}, {"kod": "20-pro", "klucz": "prz"}, {"kod": "21-ecc", "klucz": "kzn"}, {"kod": "22-can", "klucz": "pnp"}, {"kod": "23-esa", "klucz": "iz"}, {"kod": "24-ier", "klucz": "jr"}, {"kod": "25-lam", "klucz": "lm"}, {"kod": "26-eze", "klucz": "ez"}, {"kod": "27-dan", "klucz": "dn"}, {"kod": "28-ose", "klucz": "oz"}, {"kod": "29-ioe", "klucz": "jl"}, {"kod": "30-amo", "klucz": "am"}, {"kod": "31-abd", "klucz": "abd"}, {"kod": "32-ion", "klucz": "jon"}, {"kod": "33-mic", "klucz": "mi"}, {"kod": "34-nah", "klucz": "na"}, {"kod": "35-hab", "klucz": "ha"}, {"kod": "36-sop", "klucz": "so"}, {"kod": "37-agg", "klucz": "ag"}, {"kod": "38-zac", "klucz": "za"}, {"kod": "39-mal", "klucz": "ml"}, {"kod": "40-mat", "klucz": "mt"}, {"kod": "41-mar", "klucz": "mk"}, {"kod": "42-luc", "klucz": "łk"}, {"kod": "43-joh", "klucz": "j"}, {"kod": "44-act", "klucz": "dz"}, {"kod": "45-rom", "klucz": "rz"}, {"kod": "46-cor", "klucz": "1kor"}, {"kod": "47-cor", "klucz": "2kor"}, {"kod": "48-gal", "klucz": "ga"}, {"kod": "49-eph", "klucz": "ef"}, {"kod": "50-phi", "klucz": "flp"}, {"kod": "51-col", "klucz": "kol"}, {"kod": "52-the", "klucz": "1tes"}, {"kod": "53-the", "klucz": "2tes"}, {"kod": "54-tim", "klucz": "1tm"}, {"kod": "55-tim", "klucz": "2tm"}, {"kod": "56-tit", "klucz": "tt"}, {"kod": "57-phi", "klucz": "flm"}, {"kod": "58-heb", "klucz": "hbr"}, {"kod": "59-jac", "klucz": "jk"}, {"kod": "60-pet", "klucz": "1p"}, {"kod": "61-pet", "klucz": "2p"}, {"kod": "62-joh", "klucz": "1j"}, {"kod": "63-joh", "klucz": "2j"}, {"kod": "64-joh", "klucz": "3j"}, {"kod": "65-jud", "klucz": "jud"}, {"kod": "66-apo", "klucz": "ap"}];

function zloz(tekst) {
  return tekst.toLowerCase().normalize("NFD").replace(/\p{M}/gu, "").replaceAll("y", "i").replaceAll("ſ", "s").replaceAll("ƺ", "sz");
}

function dopelnij(liczba, szerokosc) {
  return String(liczba).padStart(szerokosc, "0");
}

function znajdz(tekst) {
  const linia = tekst.trim();
  let trafienie = linia.match(/^(\d{2}-[a-z]+)\s+(\d+):(\d+)$/i);
  if (trafienie) {
    return "w/" + trafienie[1].toLowerCase() + "/" + dopelnij(trafienie[2], 2) + "/" + dopelnij(trafienie[3], 3) + ".html";
  }
  trafienie = linia.match(/^(\d{2}-[a-z]+)\s+(\d+)$/i);
  if (trafienie) {
    return "k/" + trafienie[1].toLowerCase() + "/" + dopelnij(trafienie[2], 2) + ".html";
  }
  trafienie = linia.match(/^(\d{2}-[a-z]+)$/i);
  if (trafienie) {
    return "k/" + trafienie[1].toLowerCase() + "/index.html";
  }
  const zwarte = zloz(linia.replace(/\s+/g, ""));
  const skroty = KSIEGI.slice().sort((a, b) => b.klucz.length - a.klucz.length);
  for (const ksiega of skroty) {
    if (!zwarte.startsWith(ksiega.klucz)) continue;
    const reszta = zwarte.slice(ksiega.klucz.length);
    if (!reszta) return "k/" + ksiega.kod + "/index.html";
    trafienie = reszta.match(/^(\d+)[,:](\d+)$/);
    if (trafienie) {
      return "w/" + ksiega.kod + "/" + dopelnij(trafienie[1], 2) + "/" + dopelnij(trafienie[2], 3) + ".html";
    }
    trafienie = reszta.match(/^(\d+)$/);
    if (trafienie) return "k/" + ksiega.kod + "/" + dopelnij(trafienie[1], 2) + ".html";
    return null;
  }
  return null;
}

document.getElementById("skok").addEventListener("submit", (zdarzenie) => {
  zdarzenie.preventDefault();
  const cel = znajdz(document.getElementById("adres").value);
  const blad = document.getElementById("skok-blad");
  if (!cel) {
    blad.hidden = false;
    blad.textContent = "Nie ma takiego adresu. Przykład: Ps 22,17 albo 19-psa 22:17.";
    return;
  }
  blad.hidden = true;
  window.location.href = document.body.dataset.korzen + cel;
});
